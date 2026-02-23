#  Copyright (c) 2022 Piruin P.

from odoo import models, tools


class EncounterObservationLatest(models.Model):
    _name = "ni.patient.observation"
    _description = "Patient Latest Observation"
    _auto = False
    _inherit = ["ni.observation.report"]

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT DISTINCT ON (patient_id, type_id) *
            FROM ni_observation
            WHERE value IS NOT NULL
            ORDER BY patient_id, type_id, occurrence DESC
        )
        """
            % (self._table)
        )
