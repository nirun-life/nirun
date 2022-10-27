#  Copyright (c) 2022. NSTDA
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_vaccine = fields.Boolean(compute="_compute_is_vaccine")
    vaccine_count = fields.Integer(compute="_compute_is_vaccine")

    def _compute_is_vaccine(self):
        vacc = self.env["ni.vaccine"].read_group(
            [("product_tmpl_id", "in", self.ids)],
            ["product_tmpl_id"],
            ["product_tmpl_id"],
        )
        result = {v["product_tmpl_id"][0]: v["product_tmpl_id_count"] for v in vacc}
        for rec in self:
            rec.vaccine_count = result.get(rec.id, 0)
            rec.is_vaccine = rec.vaccine_count > 0
