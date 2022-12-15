#  Copyright (c) 2022. NSTDA
from odoo import models


class Encounter(models.Model):
    _inherit = "ni.encounter"
    _order = "period_start DESC"

    def action_dummy(self):
        return {}
