#  Copyright (c) 2021 Piruin P.

from odoo import models


class EncounterDischarge(models.Model):
    _name = "ni.encounter.discharge"
    _description = "Discharge Disposition"
    _inherit = ["coding.base"]
