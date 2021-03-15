#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class PatientCategory(models.Model):
    _name = "ni.patient.category"
    _description = "Patient Category"
    _inherit = ["coding.base"]

    patient_ids = fields.Many2many(
        "ni.patient",
        "patient_category_rel",
        "category_id",
        "patient_id",
        string="Patients",
    )
