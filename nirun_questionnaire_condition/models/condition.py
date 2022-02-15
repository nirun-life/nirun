#  Copyright (c) 2022 Piruin P.

from odoo import api, fields, models


class Condition(models.Model):
    _inherit = "ni.condition"

    survey_id = fields.Many2one(related="code_id.survey_id")
    response_ids = fields.Many2many(
        "survey.user_input",
        "ni_condition_survey_user_input",
        "condition_id",
        "user_input_id",
        domain=[("state", "=", "done"), ("test_entry", "=", False)],
    )
    response_id = fields.Many2one(
        "survey.user_input",
        "Latest Response",
        compute="_compute_response_id",
        stored=True,
        help="Latest related survey response",
    )

    @api.depends("response_ids")
    def _compute_response_id(self):
        responses = self.env["survey.user_input"].sudo()
        for rec in self:
            rec.response_id = responses.search(
                [
                    ("patient_id", "=", rec.patient_id.id),
                    ("survey_id", "=", rec.survey_id.id),
                    ("state", "=", "done"),
                    ("test_entry", "=", False),
                ],
                limit=1,
                order="create_date desc",
            )
