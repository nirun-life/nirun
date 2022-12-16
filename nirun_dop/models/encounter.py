#  Copyright (c) 2022. NSTDA
from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"
    _order = "period_start DESC,name DESC"

    priority = fields.Selection(groups="base.group_no_one")
    pre_admit_identifier = fields.Char(groups="base.group_no_one")

    def action_dummy(self):
        return {}
