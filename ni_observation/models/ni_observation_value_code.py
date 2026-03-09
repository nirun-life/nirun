#  Copyright (c) 2021 NSTDA
from odoo import fields, models


class ObservationValueCode(models.Model):
    _name = "ni.observation.value.code"
    _description = "Observation Category"
    _inherit = ["ni.coding"]

    type_ids = fields.Many2many(
        "ni.observation.type",
        "ni_observation_type_value_code_rel",
        "value_id",
        "type_id",
        required=False,
        ondelete="cascade",
    )
