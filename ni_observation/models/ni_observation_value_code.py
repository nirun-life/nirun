#  Copyright (c) 2021 NSTDA
from odoo import _, api, fields, models


class ObservationValueCode(models.Model):
    _name = "ni.observation.value.code"
    _description = "Observation Category"
    _inherit = ["ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one(
        "ni.observation.value.code", index=True, ondelete="set null"
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many("ni.observation.value.code", "parent_id", index=True)

    type_ids = fields.Many2many(
        "ni.observation.type",
        "ni_observation_type_value_code_rel",
        "value_id",
        "type_id",
        required=False,
        ondelete="cascade",
    )

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
