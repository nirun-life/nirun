#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class ObservationType(models.Model):
    _name = "ni.observation.type"
    _description = "Observation Type"
    _inherit = ["coding.base"]

    category_id = fields.Many2one("ni.observation.category", index=True)
    min = fields.Float()
    max = fields.Float(default=100.0)
    unit = fields.Many2one("ni.quantity.unit", index=True, required=False)
    ref_range_ids = fields.One2many(
        "ni.observation.reference.range", "type_id", "Reference Range"
    )
    ref_range_count = fields.Integer(
        compute="_compute_ref_range_count", sudo_compute=True, store=True
    )

    @api.depends("ref_range_ids")
    def _compute_ref_range_count(self):
        ref_range = self.env["ni.observation.reference.range"].sudo()
        read = ref_range.read_group(
            [("type_id", "in", self.ids)], ["type_id"], ["type_id"]
        )
        data = {res["type_id"][0]: res["type_id_count"] for res in read}
        for rec in self:
            rec.ref_range_count = data.get(rec.id, 0)
