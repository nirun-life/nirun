#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class DiagnosisRole(models.Model):
    _name = "ni.encounter.diagnosis.role"
    _description = "Diagnosis Role"
    _inherit = ["ni.coding"]

    limit = fields.Integer(default=-1)
    decoration = fields.Selection(
        [
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("muted", "Muted"),
        ],
        default="muted",
        required=True,
    )
