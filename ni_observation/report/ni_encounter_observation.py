#  Copyright (c) 2022 Piruin P.

from odoo import models, tools


class EncounterObservationLatest(models.Model):
    _name = "ni.encounter.observation"
    _description = "Encounter Latest Observation"
    _auto = False
    _inherit = ["ni.observation.report"]

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT *
            FROM ni_observation
            WHERE id IN (
                SELECT max(id)
                FROM ni_observation
                WHERE value IS NOT NULL
                GROUP BY encounter_id, type_id
            )
        )
        """
            % (self._table)
        )
