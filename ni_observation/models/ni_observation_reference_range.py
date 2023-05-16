#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReferenceRange(models.Model):
    _name = "ni.observation.reference.range"
    _description = "Observation Reference Range"
    _order = "type_id, low"

    type_id = fields.Many2one("ni.observation.type", index=True, required=True)
    low = fields.Float(help="Inclusive")
    high = fields.Float(help="Exclusive")
    interpretation_id = fields.Many2one("ni.observation.interpretation", required=True)
    active = fields.Boolean(default="True")

    def name_get(self):
        return [
            (ref.id, "%s [%d-%d]" % (ref.type_id.name, ref.low, ref.high))
            for ref in self
        ]

    @api.constrains("low", "high")
    def _validate_low_high(self):
        for rec in self:
            if rec.low > rec.high:
                raise ValidationError(_("low value must not be more than high value"))
