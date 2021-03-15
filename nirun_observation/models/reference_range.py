#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class ReferenceRange(models.Model):
    _name = "ni.observation.reference.range"
    _description = "Observation Reference Range"
    _order = "observation, low"

    observation = fields.Selection(
        [
            ("bp-s", "Blood Pressure Systolic"),
            ("bp-d", "Blood Pressure Diastolic"),
            ("body-temp", "Body Temperature"),
        ],
        required=True,
        index=True,
    )
    low = fields.Float(help="Inclusive")
    high = fields.Float(help="Exclusive")
    interpretation_id = fields.Many2one("ni.observation.interpretation", required=True)

    def name_get(self):
        return [
            (ref.id, "%s [%d-%d]" % (ref.observation, ref.low, ref.high))
            for ref in self
        ]
