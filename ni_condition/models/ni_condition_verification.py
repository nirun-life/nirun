#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class ConditionCode(models.Model):
    _name = "ni.condition.verification"
    _description = "Condition Verification"
    _inherit = ["ni.coding"]

    parent_id = fields.Many2one(
        "ni.condition.verification", index=True, ondelete="set null"
    )

    @api.depends("name", "parent_id.name")
    def _compute_display_name(self):
        for rec in self:
            name = rec.name or ""
            if rec.parent_id:
                name = f"{rec.parent_id.name}, {rec.name}"
            rec.display_name = name

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
