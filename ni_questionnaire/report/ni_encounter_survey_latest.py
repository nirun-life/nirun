#  Copyright (c) 2022 Piruin P.

from odoo import models, tools


class EncounterSurveyLatest(models.Model):
    _name = "ni.encounter.survey_latest"
    _description = "Encounter's latest survey result"
    _inherit = ["ni.patient.survey_latest"]
    _auto = False

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT DISTINCT ON (encounter_id, survey_id) *
            FROM survey_user_input
            WHERE state = 'done' AND encounter_id IS NOT NULL
            ORDER BY encounter_id, survey_id, create_date DESC
        )
        """
            % (self._table)
        )
