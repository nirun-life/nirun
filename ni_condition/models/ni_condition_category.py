#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class ConditionCategory(models.Model):
    _name = "ni.condition.category"
    _description = "Condition Category"
    _inherit = "ni.coding"

    _parent_store = True

    parent_id = fields.Many2one(
        "ni.condition.category", index=True, ondelete="set null"
    )
    parent_path = fields.Char(index=True, unaccent=False)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
