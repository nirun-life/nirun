#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    related_person_ids = fields.One2many("ni.patient.related.person", "patient_id")
    related_person_count = fields.Integer(compute="_compute_related_person_count")

    @api.depends("related_person_ids")
    def _compute_related_person_count(self):
        for rec in self:
            rec.related_person_count = len(rec.related_person_ids)
