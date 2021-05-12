#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    response_ids = fields.One2many(
        "survey.user_input",
        "patient_id",
        domain=[("state", "=", "done")],
        help="Completed survey's response",
    )
    response_count = fields.Integer(
        compute="_compute_response_count", sudo_compute=True
    )

    @api.depends("response_ids")
    def _compute_response_count(self):
        for rec in self:
            rec.response_count = len(rec.response_ids)

    def action_survey_user_input_completed(self):
        action_rec = self.env.ref("survey.action_survey_user_input")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.ids[0],
                "search_default_completed": 1,
                "search_default_not_test": 1,
                "search_default_group_by_survey": 1,
            }
        )
        action["context"] = ctx
        return action
