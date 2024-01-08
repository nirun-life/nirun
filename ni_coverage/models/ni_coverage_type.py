#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models


class CoverageType(models.Model):
    _name = "ni.coverage.type"
    _description = "Coverage Type"
    _inherit = ["ni.coding"]
    _parent_store = True
    _rec_names_search = ["name", "parent_id", "code"]

    parent_id = fields.Many2one("ni.coverage.type", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many("ni.coverage.type", "parent_id")
    child_count = fields.Integer(compute="_compute_child_count", store=True)

    kind = fields.Selection(
        [("insurance", "Insurance"), ("self-pay", "Self-Pay"), ("other", "Other")],
        default="insurance",
        required=True,
    )

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        coverage = self
        name = coverage.name or ""
        if coverage.parent_id and coverage.parent_id.name not in name:
            name = "{} {}".format(coverage.parent_id.name, name)
        if self._context.get("show_code"):
            code = (
                "{}/{}".format(coverage.parent_id.code, coverage.code)
                if coverage.parent_id
                else coverage.code
            )
            name = "{} [{}]".format(name, code)
        return name

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

    @api.depends("child_ids")
    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)
