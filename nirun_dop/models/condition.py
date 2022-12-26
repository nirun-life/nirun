#  Copyright (c) 2022. NSTDA
from odoo import fields, models


class Condition(models.Model):
    _inherit = "ni.condition"

    classification_id = fields.Many2one(groups="base.group_no_one")
    severity = fields.Selection(groups="base.group_no_one")
    verification_id = fields.Many2one(groups="base.group_no_one")
