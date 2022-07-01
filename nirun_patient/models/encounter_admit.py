#  Copyright (c) 2021 NSTDA

from odoo import models


class EncounterAdmitSource(models.Model):
    _name = "ni.encounter.admit"
    _description = "Admit Source"
    _inherit = ["coding.base"]
