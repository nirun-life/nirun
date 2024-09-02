#  Copyright (c) 2021 NSTDA
from odoo import api, fields, models


class ObservationValueCode(models.Model):
    _name = "ni.observation.value.code"
    _description = "Observation Category"
    _inherit = ["ni.coding"]

    type_id = fields.Many2one("ni.observation.type")
    type_ids = fields.Many2many(
        "ni.observation.type",
        "ni_observation_type_value_code_rel",
        "value_id",
        "type_id",
        required=False,
        ondelete="cascade",
    )

    @api.constrains("type_id", "type_ids")
    def _check_type_id(self):
        for rec in self:
            if rec.type_id and rec.type_id not in rec.type_ids:
                rec.type_ids = [fields.Command.link(rec.type_id.id)]
