#  Copyright (c) 2021 NSTDA

from odoo import models


class DosageSite(models.Model):
    _name = "ni.medication.dosage.site"
    _description = "Body Site"
    _inherit = ["coding.base"]
