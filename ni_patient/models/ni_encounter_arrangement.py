#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class EncounterSpecialArrangement(models.Model):
    _name = "ni.encounter.arrangement"
    _description = "Special arrangements"
    _inherit = ["ni.coding"]
