#  Copyright (c) 2021-2023 NSTDA
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    allergy_ids = fields.One2many("ni.allergy", "patient_id", check_company=True)
    allergy_code_ids = fields.Many2many(
        "ni.allergy.code",
        string="Allergy / Intolerance",
        compute="_compute_allergy",
    )
    allergy_count = fields.Integer(compute="_compute_allergy")

    @api.depends("allergy_ids")
    def _compute_allergy(self):
        for rec in self:
            rec.allergy_count = len(rec.allergy_ids)
            rec.allergy_code_ids = rec.allergy_ids.mapped("code_id")
