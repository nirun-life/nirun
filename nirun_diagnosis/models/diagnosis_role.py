#  Copyright (c) 2023-2023. NSTDA

from odoo import fields, models


class DiagnosisRole(models.Model):
    _name = "ni.diagnosis.role"
    _description = "Diagnosis Role"
    _inherit = ["coding.base"]

    limit = fields.Integer(default=-1)
