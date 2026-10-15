#  Copyright (c) 2026 NSTDA
"""Move Nirun's units of measure to the 19.0 UoM model.

Odoo 19 drops ``uom.category``, ``factor`` (now computed) and ``uom_type``: a unit is
``relative_factor`` times its ``relative_uom_id``. OpenUpgrade 19 (``uom``) copies the
old columns to ``openupgrade_legacy_19_0_*`` but converts only units without an xmlid;
units created by a module are left to that module. Every unit of ``ni_observation``
has an xmlid and ``data/uom_uom_data.xml`` is ``noupdate``, so convert them here:

- a 16.0-18.0 reference unit becomes a root unit (no ``relative_uom_id``, factor 1);
- any other unit points to the reference unit of its old category with
  ``relative_factor = 1 / factor``, which keeps every conversion the same.

The old categories' xmlids are dropped, as the model no longer exists.
Without the OpenUpgrade legacy columns (no OpenUpgrade run) this does nothing.
"""

import logging

from psycopg2 import sql

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

LEGACY = "openupgrade_legacy_19_0_"


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """
        SELECT count(*) FROM information_schema.columns
        WHERE table_name = 'uom_uom' AND column_name IN %s
        """,
        (tuple(LEGACY + c for c in ("category_id", "factor", "uom_type")),),
    )
    if cr.fetchone()[0] != 3:
        _logger.info("No OpenUpgrade legacy UoM columns: nothing to convert")
        return
    cr.execute(
        sql.SQL(
            """
            SELECT u.id, u.{factor}, u.{uom_type},
                (
                    SELECT r.id FROM uom_uom r
                    WHERE r.{category} = u.{category}
                    AND r.{uom_type} = 'reference'
                    ORDER BY r.active DESC, r.id
                    LIMIT 1
                )
            FROM uom_uom u
            JOIN ir_model_data d
                ON d.model = 'uom.uom'
                AND d.res_id = u.id
                AND d.module = 'ni_observation'
            WHERE u.{category} IS NOT NULL
            """
        ).format(
            factor=sql.Identifier(LEGACY + "factor"),
            uom_type=sql.Identifier(LEGACY + "uom_type"),
            category=sql.Identifier(LEGACY + "category_id"),
        )
    )
    rows = cr.fetchall()
    env = api.Environment(cr, SUPERUSER_ID, {})
    for uom_id, factor, uom_type, reference_id in rows:
        uom = env["uom.uom"].browse(uom_id)
        if uom_type == "reference" or not reference_id or reference_id == uom_id:
            uom.write({"relative_uom_id": False, "relative_factor": 1.0})
        else:
            uom.write(
                {"relative_uom_id": reference_id, "relative_factor": 1.0 / factor}
            )
    _logger.info("Converted %s ni_observation units of measure", len(rows))
    cr.execute(
        "DELETE FROM ir_model_data "
        "WHERE module = 'ni_observation' AND model = 'uom.category'"
    )
