#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


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
            (ref.id, "%s [%d-%d]" % (ref.observation, ref.low, ref.high))
            for ref in self
        ]
