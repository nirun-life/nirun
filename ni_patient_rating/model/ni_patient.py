#  Copyright (c) 2026 NSTDA
from odoo import models


class Patient(models.Model):
    _name = "ni.patient"
    _inherit = ["ni.patient", "rating.parent.mixin"]
