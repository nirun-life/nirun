#  Copyright (c) 2021-2023 NSTDA
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_medication = fields.Boolean(compute="_compute_is_medication")
    medication_count = fields.Integer(compute="_compute_is_medication")

    def _compute_is_medication(self):
        medi = self.env["ni.medication"].read_group(
            [("product_tmpl_id", "in", self.ids)],
            ["product_tmpl_id"],
            ["product_tmpl_id"],
        )
        result = {m["product_tmpl_id"][0]: m["product_tmpl_id_count"] for m in medi}
        for rec in self:
            rec.medication_count = result.get(rec.id, 0)
            rec.is_medication = rec.medication_count > 0
