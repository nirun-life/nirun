#  Copyright (c) 2022 Piruin P.

from odoo import fields, models


class Goal(models.Model):
    _inherit = "ni.goal"

    careplan_id = fields.Many2one(
        "ni.careplan", required=False, index=True, ondelete="cascade", copy=False
    )
