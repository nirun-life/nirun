#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Religion(models.Model):
    _inherit = "res.religion"
    _order = "patient_count DESC, name"

    patient_ids = fields.One2many("ni.patient", "religion", readonly=True)
    patient_count = fields.Integer(compute="_compute_patient_count", store=True)

    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for religion in self:
            religion.patient_count = len(religion.patient_ids)
