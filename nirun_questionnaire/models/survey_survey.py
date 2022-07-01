#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    subject_type = fields.Selection(
        selection_add=[("ni.patient", "Patient"), ("ni.encounter", "Encounter")]
    )
    category = fields.Selection(
        selection_add=[
            ("ni_patient", "Patient Questionnaire"),
            ("ni_encounter", "Encounter Questionnaire"),
        ]
    )

    @api.onchange("category")
    def _onchange_category(self):
        for rec in self:
            if rec.category.startswith("ni_"):
                rec.subject_type = rec.category.replace("_", ".")
                rec.access_mode = "token"
                rec.users_login_required = True
