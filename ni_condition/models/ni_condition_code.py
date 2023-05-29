#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class ConditionCode(models.Model):
    _name = "ni.condition.code"
    _description = "Condition / Problem"
    _inherit = ["ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("ni.condition.code", index=True, ondelete="cascade")
    parent_path = fields.Char(index=True, unaccent=False)

    class_id = fields.Many2one("ni.condition.class", required=False)

    _sql_constraints = [
        (
            "system_name_uniq",
            "unique (system_id, parent_id, name)",
            "This name already exists!",
        ),
    ]

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
