#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class ConditionCode(models.Model):
    _name = "ni.condition.code"
    _description = "Condition / Problem"
    _inherit = ["coding.base"]

    type_id = fields.Many2one("ni.condition.type", required=False)
    category = fields.Selection(
        [
            ("problem-list-item", "Problem List Item"),
            ("encounter-diagnosis", "Encounter Diagnosis"),
        ],
        required=False,
        help="Make this condition selectable for category ",
    )
