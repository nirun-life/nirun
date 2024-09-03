#  Copyright (c) 2021 NSTDA
from odoo import api, fields, models


class ObservationType(models.Model):
    _name = "ni.observation.category"
    _description = "Observation Category"
    _inherit = ["ni.coding"]

    type_ids = fields.One2many("ni.observation.type", "category_id")
    type_count = fields.Integer(compute="_compute_type_count", store=True)

    @api.depends("type_ids")
    def _compute_type_count(self):
        for rec in self:
            rec.type_count = len(rec.type_ids)
