#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    subject_type = fields.Selection(selection_add=[("ni.patient", "Patient")])
    category = fields.Selection(
        selection_add=[("patient", "Patient's health Assessment")]
    )

    @api.onchange("category")
    def _onchange_category(self):
        for rec in self:
            if rec.category == "patient":
                rec.subject_type = "ni.patient"
                rec.access_mode = "token"
                rec.users_login_required = True
