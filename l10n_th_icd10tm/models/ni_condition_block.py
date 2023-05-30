#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class ConditionBlock(models.Model):
    _name = "ni.condition.block"
    _description = "Block"
    _inherit = "ni.coding"
    _parent_store = True

    chapter_id = fields.Many2one("ni.condition.chapter")
    parent_id = fields.Many2one("ni.condition.block", index=True, ondelete="cascade")
    parent_path = fields.Char(index=True, unaccent=False)
    level = fields.Integer(default=1)
    code_ids = fields.One2many("ni.condition.code", "block_id", "item")

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
