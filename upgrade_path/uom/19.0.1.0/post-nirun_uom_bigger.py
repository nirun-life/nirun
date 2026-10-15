#  Copyright (c) 2026 NSTDA
"""Fix the ratio of user-created "bigger" units of measure.

Odoo 19 defines a unit as ``relative_factor`` times its reference unit. Up to 18.0
one reference unit equalled ``factor`` of the unit, for every ``uom_type`` (a "bigger"
unit had ``factor`` < 1, for example a dozen: 1/12). So ``relative_factor`` must be
``1 / factor`` for every type. OpenUpgrade 19 (``uom/19.0.1.0/post-migration.py``)
uses ``factor`` as is for "bigger" units, which inverts their ratio: a "Box of 24"
becomes 1/24 of a unit.

OpenUpgrade only converts units without an xmlid, so fix those "bigger" units here.
This script runs after OpenUpgrade's ``post-migration.py`` (scripts run by name).
Upstream fix: https://github.com/OCA/OpenUpgrade/pull/6054; drop this script once it
is merged (it is then a no-op: it only rewrites the same values).
"""

from openupgradelib import openupgrade
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    names = {c: openupgrade.get_legacy_name(c) for c in ("factor", "uom_type")}
    if not all(openupgrade.column_exists(cr, "uom_uom", n) for n in names.values()):
        return
    cr.execute(
        sql.SQL(
            """
            SELECT u.id, 1.0 / u.{factor}
            FROM uom_uom u
            WHERE u.{uom_type} = 'bigger'
            AND u.{factor} > 0
            AND u.relative_uom_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM ir_model_data d
                WHERE d.model = 'uom.uom'
                AND d.res_id = u.id
                AND d.module != '__export__'
            )
            """
        ).format(
            factor=sql.Identifier(names["factor"]),
            uom_type=sql.Identifier(names["uom_type"]),
        )
    )
    for uom_id, relative_factor in cr.fetchall():
        env["uom.uom"].browse(uom_id).write({"relative_factor": relative_factor})
