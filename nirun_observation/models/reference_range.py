#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class ReferenceRange(models.Model):
    _name = "ni.observation.reference.range"
    _description = "Observation Reference Range"
    _order = "type_id, low"

    type_id = fields.Many2one("ni.observation.type", index=True, required=True)
    low = fields.Float(help="Inclusive")
    high = fields.Float(help="Exclusive")
    interpretation_id = fields.Many2one("ni.observation.interpretation", required=True)

    def name_get(self):
        return [
            (ref.id, "%s [%d-%d]" % (ref.observation, ref.low, ref.high))
            for ref in self
        ]

    @api.model
    def match_for(self, observation, value):
        return self.search(
            [
                ("type_id", "=", observation),
                ("low", "<=", value),
                ("high", ">", value),
            ],
            limit=1,
        )
