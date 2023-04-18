#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class EncounterAdmitSource(models.Model):
    _name = "ni.encounter.admit"
    _description = "Admit Source"
    _inherit = ["ni.coding"]
