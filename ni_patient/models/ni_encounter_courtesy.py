#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class EncounterSpecialCourtesy(models.Model):
    _name = "ni.encounter.courtesy"
    _description = "Special Courtesy"
    _inherit = ["ni.coding"]
