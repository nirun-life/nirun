#  Copyright (c) 2022. NSTDA

from odoo import api, fields, models


class Vaccine(models.Model):
    _name = "ni.vaccine"
    _inherit = ["coding.base"]
    _inherits = {"product.template": "product_tmpl_id"}
    _description = "Vaccine"

    product_tmpl_id = fields.Many2one(
        "product.template",
        "Product Template",
        auto_join=True,
        index=True,
        ondelete="cascade",
        required=True,
        tracking=True,
    )
    manufacturer_ids = fields.Many2many(
        "res.partner", domain=[("is_company", "=", True)], tracking=True
    )
    manufacturer_filter = fields.Integer(compute="_compute_manufacturer_filter")

    @api.depends("manufacturer_ids")
    def _compute_manufacturer_filter(self):
        for rec in self:
            rec.manufacturer_filter = 2147483647 if rec.manufacturer_ids else 0
