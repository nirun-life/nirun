#  Copyright (c) 2026 NSTDA
"""Hand partner titles over from core ``base`` (up to 18.0) to OCA ``partner_title``.

Odoo 19 dropped the ``res.partner.title`` model and the partner ``title`` field.
OpenUpgrade keeps the table and the column but does not move them anywhere, and
``partner_title`` (a dependency of ``partner_gender``) then fails to install
because its data collides with the existing rows. This runs in the ``base`` pre
stage, before ``partner_title`` is installed, so the module adopts the existing
data instead.
"""

from openupgradelib import openupgrade

TITLES = ["madam", "miss", "mister", "doctor", "prof"]
TITLE_FIELDS = [
    "id",
    "name",
    "shortcut",
    "display_name",
    "create_uid",
    "create_date",
    "write_uid",
    "write_date",
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.table_exists(cr, "res_partner_title"):
        return
    if not openupgrade.is_module_installed(cr, "partner_gender"):
        return
    xmlids = [
        (f"base.res_partner_title_{title}", f"partner_title.res_partner_title_{title}")
        for title in TITLES
    ]
    xmlids.append(
        ("base.model_res_partner_title", "partner_title.model_res_partner_title")
    )
    xmlids += [
        (
            f"base.field_res_partner_title__{field}",
            f"partner_title.field_res_partner_title__{field}",
        )
        for field in TITLE_FIELDS
    ]
    xmlids.append(
        ("base.field_res_partner__title", "partner_title.field_res_partner__title_id")
    )
    openupgrade.rename_xmlids(cr, xmlids)
    if openupgrade.column_exists(cr, "res_partner", "title"):
        openupgrade.rename_fields(
            env, [("res.partner", "res_partner", "title", "title_id")]
        )
