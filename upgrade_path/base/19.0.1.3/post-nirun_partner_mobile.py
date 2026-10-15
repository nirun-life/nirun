#  Copyright (c) 2026 NSTDA
"""Keep partner phone and mobile apart when Nirun restores ``mobile``.

Odoo 19 dropped ``res.partner.mobile``. OpenUpgrade 19 keeps the ``mobile`` column
but appends the mobile number to ``phone`` ("phone // mobile"), after copying the
original phone to a legacy column. ``ni_patient`` depends on
``ni_partner_mobile``, which brings the ``mobile`` field back on the kept column, so
the merged phone would show the mobile number twice: put the original phone back.
This runs after OpenUpgrade's own ``base`` post-migration.
"""

from openupgradelib import openupgrade
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.is_module_installed(cr, "ni_patient"):
        return
    legacy_phone = openupgrade.get_legacy_name("phone")
    if not openupgrade.column_exists(cr, "res_partner", legacy_phone):
        return
    openupgrade.logged_query(
        cr,
        sql.SQL(
            """
            UPDATE res_partner
            SET phone = {legacy}
            WHERE COALESCE(mobile, '') != ''
            AND phone IS DISTINCT FROM {legacy}
            """
        ).format(legacy=sql.Identifier(legacy_phone)),
    )
