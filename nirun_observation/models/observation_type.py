#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class ObservationType(models.Model):
    _name = "ni.observation.type"
    _description = "Observation Type"
    _inherit = ["coding.base"]

    category_id = fields.Many2one("ni.observation.category", index=True)
    min = fields.Float()
    max = fields.Float()
    unit = fields.Many2one("ni.quantity.unit", index=True, required=False)
