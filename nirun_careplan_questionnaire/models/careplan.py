#  Copyright (c) 2022 Piruin P.

from odoo import api, fields, models


class CareplanGoal(models.Model):
    _inherit = "ni.careplan"

    survey_ids = fields.Many2many(
        "survey.survey",
        "ni_careplan_survey_rel",
        "careplan_id",
        "survey_id",
        compute="_compute_surveys_ids",
        copy=False,
    )
    survey_pre_response_ids = fields.Many2many(
        "survey.user_input",
        "ni_careplan_survey_pre_response_rel",
        "careplan_id",
        "survey_user_input_id",
        "Survey (Pre)",
        copy=False,
    )
    survey_post_response_ids = fields.Many2many(
        "survey.user_input",
        "ni_careplan_survey_post_response_rel",
        "careplan_id",
        "survey_user_input_id",
        "Survey (Post)",
        copy=False,
        readonly=True,
        states={"completed": [("readonly", False)]},
    )

    @api.depends("survey_pre_response_ids")
    def _compute_surveys_ids(self):
        for rec in self:
            if rec.survey_pre_response_ids:
                rec.survey_ids = rec.survey_pre_response_ids.mapped("survey_id")
            else:
                rec.survey_ids = None
