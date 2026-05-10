# pylint: disable=print-used
import base64
import importlib
import os
import sys

# 'env' is injected by the Odoo shell via exec() — pull it from globals so
# static analysis tools see it as a defined name.
env = globals().get("env")
if env is None:
    print(
        "ERROR: run via  python odoo-bin shell -c odoo.conf -d <db> --no-http < export_po.py",
        file=sys.stderr,
    )
    sys.exit(1)

# --- configuration (override with env vars) ---
module_name = os.environ.get("ODOO_MODULE", "ni_patient")
lang_code = os.environ.get("ODOO_LANG", "th_TH")

# --- resolve module path from Odoo addon registry (cross-machine) ---
try:
    addon = importlib.import_module(f"odoo.addons.{module_name}")
    module_dir = os.path.dirname(addon.__file__)
except ImportError:
    print(
        f"ERROR: cannot import odoo.addons.{module_name} — is it on addons_path?",
        file=sys.stderr,
    )
    sys.exit(1)

# --- check module exists in database ---
module_rec = env["ir.module.module"].search([("name", "=", module_name)], limit=1)
if not module_rec:
    print(f"ERROR: module '{module_name}' not found in database", file=sys.stderr)
    sys.exit(1)

# --- export ---
export = env["base.language.export"].create(
    {
        "lang": lang_code,
        "format": "po",
        "modules": [(6, 0, [module_rec.id])],
        "state": "choose",
    }
)
export.act_getfile()

# --- write to <module>/i18n/<lang>.po  (e.g. th_TH -> th.po) ---
lang_short = lang_code.split("_")[0]
i18n_dir = os.path.join(module_dir, "i18n")
os.makedirs(i18n_dir, exist_ok=True)
out_path = os.path.join(i18n_dir, f"{lang_short}.po")

data = base64.b64decode(export.data)
with open(out_path, "wb") as f:
    f.write(data)

print(f"OK: {module_name}/i18n/{lang_short}.po — {len(data):,} bytes written")
