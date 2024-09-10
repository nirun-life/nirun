#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class ObservationType(models.Model):
    _inherit = "ni.observation.type"

    survey_id = fields.Many2one("survey.survey")


class Observation(models.AbstractModel):
    _inherit = "ni.observation.abstract"

    survey_id = fields.Many2one(related="type_id.survey_id")
    survey_response_id = fields.Many2one(
        "survey.user_input", store=True, groups="survey.group_survey_user"
    )

    def action_print_survey(self):
        """If response is available then print this response otherwise print
        survey form (print template of the survey)"""
        self.ensure_one()
        if self.survey_response_id:
            action = self.survey_response_id.survey_id.action_print_survey(
                self.survey_response_id
            )
            action["target"] = "new"
            return action
