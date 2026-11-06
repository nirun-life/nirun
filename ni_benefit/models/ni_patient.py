#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    benefit_ids = fields.Many2many(
        "ni.benefit", "ni_patient_benefit", "patient_id", "benefit_id"
    )
    benefit_count = fields.Integer(compute="_compute_benefit_count")

    @api.depends("benefit_ids")
    def _compute_benefit_count(self):
        for rec in self:
            rec.benefit_count = len(rec.benefit_ids)
