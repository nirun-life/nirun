#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CoverageType(models.Model):
    _name = "ni.coverage.type"
    _description = "Coverage Type"
    _inherit = ["ni.coding"]
    _parent_store = True
    _rec_names_search = ["name", "parent_id.name", "code", "abbr"]

    parent_id = fields.Many2one("ni.coverage.type", index=True, ondelete="set null")
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("ni.coverage.type", "parent_id")
    child_count = fields.Integer(compute="_compute_child_count", store=True)

    kind = fields.Selection(
        [("insurance", "Insurance"), ("self-pay", "Self-Pay"), ("other", "Other")],
        default="insurance",
        required=True,
    )

    @api.depends("parent_id.code")
    def _compute_display_name(self):
        for coverage_type in self:
            coverage_type.display_name = coverage_type._name_get()

    def _name_get(self):
        coverage_type = self
        parent = coverage_type.parent_id
        name = coverage_type.name or ""
        if parent and parent.name not in name:
            name = f"{parent.name} {name}"
        if self.env.context.get("show_code"):
            code = f"{parent.code}/{coverage_type.code}" if parent else self.code
            name = f"{name} [{code}]"
        return name

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(
                self.env._("Error! You cannot create recursive data.")
            )

    @api.depends("child_ids")
    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)
