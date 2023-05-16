#  Copyright (c) 2021 NSTDA
from odoo import fields, models


class ObservationType(models.Model):
    _name = "ni.observation.value.code"
    _description = "Observation Category"
    _inherit = ["ni.coding"]

    type_id = fields.Many2one("ni.observation.type", required=True, ondelete="cascade")
