#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class Need(models.Model):
    _name = "ni.need"
    _description = "Needs"
    _inherit = ["ni.coding"]


class PatientNeed(models.Model):
    _name = "ni.patient.need"
    _description = "Patient Need Line"
    _inherit = ["ni.patient.res"]
    _rec_name = "need_id"

    need_id = fields.Many2one("ni.need", required=True)
