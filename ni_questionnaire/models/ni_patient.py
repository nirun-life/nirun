#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    response_ids = fields.One2many(
        "survey.user_input",
        "patient_id",
        domain=[("state", "=", "done")],
        help="Completed survey's response",
        groups="survey.group_survey_user",
    )
    response_count = fields.Integer(
        compute="_compute_response_count",
        sudo_compute=True,
        groups="survey.group_survey_user",
    )
    response_latest_ids = fields.One2many("ni.patient.survey_latest", "patient_id")

    @api.depends("response_ids")
    def _compute_response_count(self):
        for rec in self:
            rec.response_count = len(rec.response_ids)

    def action_survey_user_input_completed(self):
        action_rec = self.env.ref(
            "ni_questionnaire.questionnaire_response_action"
        ).sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.ids[0],
                "search_default_group_by_survey": 1,
                "default_subject_ni_patient": self.id,
            }
        )
        action["context"] = ctx
        return action
