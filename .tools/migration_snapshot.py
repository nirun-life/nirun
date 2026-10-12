#  Copyright (c) 2026 NSTDA
"""Data snapshot used to prove that an OpenUpgrade step loses no data.

Run through the Odoo shell on any version from 16.0 to 19.0:

    SNAPSHOT_OUT=snap-16.json odoo-bin shell -c odoo.conf -d <db> --no-http \
        < .tools/migration_snapshot.py

Compare two snapshots with:

    diff <(jq -S . snap-16.json) <(jq -S . snap-19.json)

The output holds counts and SHA-256 hashes only, never raw personal data (PDPA).

Environment variables:

- ``SNAPSHOT_OUT``: output file; stdout when unset.
- ``SNAPSHOT_DETAIL=1``: also emit one hash per record, keyed by id.
- ``SNAPSHOT_SALT``: optional secret mixed into every hash (HMAC), so that hashes
  of low-entropy values cannot be reversed by brute force. Use the same salt for
  every snapshot that will be compared.
- ``SNAPSHOT_BATCH``: records read per batch (default 1000).
"""

# pylint: disable=print-used
import hashlib
import hmac
import json
import os
import sys
from datetime import date

# 'env' is injected by the Odoo shell via exec() — pull it from globals so
# static analysis tools see it as a defined name.
env = globals().get("env")
if env is None:
    print(
        "ERROR: run via  python odoo-bin shell -c odoo.conf -d <db> --no-http"
        " < .tools/migration_snapshot.py",
        file=sys.stderr,
    )
    sys.exit(1)

# --- configuration (override with env vars) ---
out_path = os.environ.get("SNAPSHOT_OUT", "")
detail = os.environ.get("SNAPSHOT_DETAIL", "") == "1"
salt = os.environ.get("SNAPSHOT_SALT", "").encode()
batch_size = int(os.environ.get("SNAPSHOT_BATCH", "1000"))

# Read everything, in a fixed language, without record rules or archive filters.
env = env(
    context=dict(env.context, active_test=False, lang="en_US", tz="UTC"),
    su=True,
)

# Core models extended by Phase 1 modules, counted even when no Nirun module
# defines them (see the key datasets below).
CORE_MODELS = [
    "res.partner",
    "uom.uom",
    "uom.category",
    "survey.survey",
    "survey.question",
    "survey.question.answer",
    "survey.user_input",
    "survey.user_input.line",
]

# Key datasets: (model, [(label, dotted field path)], [group-by fields]).
# A path can be a tuple of alternatives, for fields renamed between versions; the
# first one that exists is used. Paths whose field does not exist yield null.
DATASETS = [
    (
        "res.partner",
        [],
        ["type"],
    ),
    (
        "ni.patient",
        [
            ("identifier", "identifier"),
            ("name", "name"),
            ("birthdate", "birthdate"),
            ("gender", "gender"),
            # res.partner.title moved to OCA partner_title (title_id) in 19.0
            ("title", ("partner_id.title.name", "partner_id.title_id.name")),
            ("mobile", "mobile"),
            ("phone", "phone"),
        ],
        [],
    ),
    (
        "ni.encounter",
        [
            ("identifier", "identifier"),
            ("patient_id", "patient_id"),
            ("period_start", "period_start"),
            ("period_end", "period_end"),
            ("state", "state"),
            ("class_code", "class_id.code"),
        ],
        ["state"],
    ),
    (
        "ni.observation",
        [
            ("patient_id", "patient_id"),
            ("encounter_id", "encounter_id"),
            ("type_code", "type_id.code"),
            ("value_type", "value_type"),
            ("value", "value"),
            ("value_float", "value_float"),
            ("value_int", "value_int"),
            ("value_char", "value_char"),
            ("value_code", "value_code_id.code"),
            ("value_codes", "value_code_ids"),
            ("uom", "unit_id.name"),
            ("occurrence", "occurrence"),
        ],
        ["state"],
    ),
    (
        "uom.uom",
        [
            ("name", "name"),
            ("factor", "factor"),
            ("relative_factor", "relative_factor"),
            ("uom_type", "uom_type"),
            ("category", "category_id.name"),
            ("relative_uom", "relative_uom_id.name"),
        ],
        [],
    ),
    (
        "uom.category",
        [("name", "name")],
        [],
    ),
    (
        "survey.survey",
        [("title", "title"), ("subject_type", "subject_type")],
        [],
    ),
    (
        "survey.question",
        [],
        ["question_type"],
    ),
    (
        "survey.user_input",
        [
            ("scoring_percentage", "scoring_percentage"),
            ("grade", "grade_id.name"),
        ],
        ["state"],
    ),
    (
        "survey.user_input.line",
        [],
        [],
    ),
    (
        "ni.workflow.event",
        [],
        ["state"],
    ),
    (
        "ni.workflow.request",
        [],
        ["state"],
    ),
]


def _digest(text):
    data = text.encode()
    if salt:
        return hmac.new(salt, data, hashlib.sha256).hexdigest()
    return hashlib.sha256(data).hexdigest()


def _scalar(value, field):
    """Normalize one field value so it compares across Odoo versions."""
    if field.type == "boolean":
        return bool(value)
    if field.type == "many2one":
        return value.id or None
    if field.type in ("one2many", "many2many"):
        return sorted(value.ids)
    if value is False or value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    if field.type in ("float", "monetary"):
        return round(value, 6)
    return value


def _path_fields(model, path):
    """Return the field chain of a dotted path, or None if any link is missing."""
    if isinstance(path, tuple):
        for alternative in path:
            chain = _path_fields(model, alternative)
            if chain:
                return chain
        return None
    chain = []
    for name in path.split("."):
        if name not in model._fields:
            return None
        field = model._fields[name]
        chain.append(field)
        if field.relational:
            model = env[field.comodel_name]
    return chain


def _resolve(record, chain):
    value = record
    for field in chain[:-1]:
        value = value[field.name]
        if not value:
            return None
        value = value[:1]
    return _scalar(value[chain[-1].name], chain[-1])


def _is_stored_model(model):
    return not (model._abstract or model._transient or not model._auto)


def _count_by(model, field_name):
    if field_name not in model._fields or not model._fields[field_name].store:
        return None
    env.cr.execute(
        f'SELECT "{field_name}", count(*) FROM "{model._table}" GROUP BY 1'  # noqa: S608
    )
    return {str(key): count for key, count in sorted(env.cr.fetchall(), key=str)}


def _dataset(model_name, paths, group_by):
    if model_name not in env.registry:
        return None
    model = env[model_name]
    if not _is_stored_model(model):
        return None
    result = {"count": model.search_count([])}
    for field_name in group_by:
        result[f"count_by_{field_name}"] = _count_by(model, field_name)
    if not paths:
        return result

    chains = {label: _path_fields(model, path) for label, path in paths}
    result["missing_fields"] = sorted(
        label for label, chain in chains.items() if chain is None
    )
    total = hashlib.sha256()
    if salt:
        total = hmac.new(salt, digestmod=hashlib.sha256)
    per_record = {}
    ids = model.search([], order="id").ids
    for start in range(0, len(ids), batch_size):
        for record in model.browse(ids[start : start + batch_size]):
            row = [record.id] + [
                _resolve(record, chain) if chain else None for chain in chains.values()
            ]
            line = json.dumps(row, sort_keys=True, ensure_ascii=True, default=str)
            total.update(line.encode() + b"\n")
            if detail:
                per_record[str(record.id)] = _digest(line)[:16]
        env.invalidate_all()
    result["fields"] = [label for label, _path in paths]
    result["sha256"] = total.hexdigest()
    if detail:
        result["records"] = per_record
    return result


def _nirun_modules():
    modules = env["ir.module.module"].search(
        [("state", "=", "installed"), ("author", "ilike", "NSTDA")]
    )
    return {module.name: module.installed_version or "" for module in modules}


def _generic_counts(nirun):
    counts = {}
    for ir_model in env["ir.model"].search([]):
        name = ir_model.model
        if name not in env.registry:
            continue
        defined_in = {m.strip() for m in (ir_model.modules or "").split(",")}
        if not (defined_in & set(nirun)) and name not in CORE_MODELS:
            continue
        model = env[name]
        if _is_stored_model(model):
            counts[name] = model.search_count([])
    return counts


def _group_users(nirun):
    users_field = "user_ids" if "user_ids" in env["res.groups"]._fields else "users"
    xmlids = env["ir.model.data"].search(
        [("model", "=", "res.groups"), ("module", "in", list(nirun))]
    )
    result = {}
    for xmlid in xmlids:
        group = env["res.groups"].browse(xmlid.res_id).exists()
        if group:
            result[f"{xmlid.module}.{xmlid.name}"] = len(group[users_field])
    return result


def _partner_extra():
    partner = env["res.partner"]
    result = {}
    # title became title_id (OCA partner_title) in 19.0
    for key, field_names in (
        ("title", ("title", "title_id")),
        ("mobile", ("mobile",)),
        ("phone", ("phone",)),
    ):
        field_name = next((f for f in field_names if f in partner._fields), None)
        if not field_name:
            result[f"with_{key}"] = None
            continue
        # From 18.0, ("phone", "!=", False) no longer matches "": exclude it on
        # every version so the counts compare.
        if partner._fields[field_name].type == "char":
            domain = [(field_name, "not in", [False, ""])]
        else:
            domain = [(field_name, "!=", False)]
        result[f"with_{key}"] = partner.search_count(domain)
    return result


nirun_modules = _nirun_modules()
snapshot = {
    "meta": {
        "odoo_version": env["ir.module.module"]
        .search([("name", "=", "base")])
        .latest_version,
        "nirun_modules": nirun_modules,
        "detail": detail,
        "salted": bool(salt),
    },
    "counts": _generic_counts(nirun_modules),
    "datasets": {},
    "groups": _group_users(nirun_modules),
}
for model_name, paths, group_by in DATASETS:
    snapshot["datasets"][model_name] = _dataset(model_name, paths, group_by)
if snapshot["datasets"]["res.partner"]:
    snapshot["datasets"]["res.partner"].update(_partner_extra())

# The script only reads; make sure nothing computed on the way is committed.
env.cr.rollback()

output = json.dumps(snapshot, sort_keys=True, indent=1, ensure_ascii=True)
if out_path:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output + "\n")
    print(f"OK: snapshot written to {out_path}", file=sys.stderr)
else:
    print(output)
