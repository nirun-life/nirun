#  Copyright (c) 2021-2022. NSTDA

from odoo import _, api, fields, models


class ConditionCode(models.Model):
    _name = "ni.condition.verification"
    _description = "Condition Verification"
    _inherit = ["coding.base"]

    display_name = fields.Char(
        "Verification", compute="_compute_display_name", index=True
    )

    parent_id = fields.Many2one(
        "ni.condition.verification", index=True, ondelete="set null"
    )

    def name_get(self):
        return [(rec.id, rec.display_name) for rec in self]

    @api.depends("name", "parent_id")
    def _compute_display_name(self):
        for rec in self:
            name = rec.name or ""
            if rec.parent_id:
                name = "{}, {}".format(rec.parent_id.name, rec.name)
            rec.display_name = name

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
