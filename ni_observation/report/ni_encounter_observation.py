#  Copyright (c) 2022 Piruin P.

from odoo import models, tools
from odoo.tools import SQL


class EncounterObservationLatest(models.Model):
    _name = "ni.encounter.observation"
    _description = "Encounter Latest Observation"
    _auto = False
    _inherit = ["ni.observation.report"]

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            SQL(
                """CREATE OR REPLACE VIEW %s AS (
                SELECT DISTINCT ON (encounter_id, type_id) *
                FROM ni_observation
                WHERE value IS NOT NULL
                ORDER BY encounter_id, type_id, occurrence DESC, id DESC
            )""",
                SQL.identifier(self._table),
            )
        )
