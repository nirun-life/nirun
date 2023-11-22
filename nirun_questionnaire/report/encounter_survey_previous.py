#  Copyright (c) 2022 Piruin P.

from odoo import models, tools


class EncounterSurveyPrevious(models.Model):
    _name = "ni.encounter.survey_previous"
    _description = "Encounter's previous survey result"
    _inherit = ["ni.patient.survey_previous"]
    _auto = False

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            f"""CREATE OR REPLACE VIEW {self._table} AS
                WITH ranked_survey_input AS (
                    SELECT
                        ROW_NUMBER() OVER
                        (PARTITION BY encounter_id,survey_id ORDER BY id DESC) AS rn,
                        *
                    FROM survey_user_input
                )
                SELECT *
                FROM ranked_survey_input
                WHERE rn = 2
        """
        )
