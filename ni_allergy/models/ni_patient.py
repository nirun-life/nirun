#  Copyright (c) 2021-2023 NSTDA
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    allergy_ids = fields.One2many("ni.allergy", "patient_id", check_company=True)
    allergy_count = fields.Integer(compute="_compute_allergy_count")
    # NOTE Can't use code_ids pattern on patient without duplicate the codes because of
    # behavior of delegate inheritance, so Implement only apply on Encounter

    @api.depends("allergy_ids")
    def _compute_allergy_count(self):
        for rec in self:
            rec.allergy_count = len(rec.allergy_ids)
