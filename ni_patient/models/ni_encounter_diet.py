#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class EncounterDiet(models.Model):
    _name = "ni.encounter.diet"
    _description = "Diet"
    _inherit = ["ni.coding"]
