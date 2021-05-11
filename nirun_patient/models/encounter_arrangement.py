#  Copyright (c) 2021 Piruin P.

from odoo import models


class EncounterSpecialArrangement(models.Model):
    _name = "ni.encounter.arrangement"
    _description = "Special arrangements"
    _inherit = ["coding.base"]
