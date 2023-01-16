#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models


class Disability(models.Model):
    _name = "ni.disability"
    _description = "Disability Type"
    _inherit = ["coding.base"]

    patient_ids = fields.Many2many(
        "ni.patient", "ni_patient_disability_rel", "disability_id", "patient_id"
    )
    patient_count = fields.Integer(
        "Total", compute="_compute_patient_count", store=True, compute_sudo=True
    )
    patient_male_count = fields.Integer(
        "Male", compute="_compute_patient_count", store=True, compute_sudo=True
    )
    patient_female_count = fields.Integer(
        "Female", compute="_compute_patient_count", store=True, compute_sudo=True
    )

    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)
            rec.patient_male_count = len(
                rec.patient_ids.filtered(lambda p: p.gender == "male")
            )
            rec.patient_female_count = len(
                rec.patient_ids.filtered(lambda p: p.gender == "female")
            )
