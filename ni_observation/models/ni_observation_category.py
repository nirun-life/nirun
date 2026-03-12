#  Copyright (c) 2021 NSTDA
from odoo import _, api, fields, models


class ObservationType(models.Model):
    _name = "ni.observation.category"
    _description = "Observation Category"
    _inherit = ["ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("ni.observation.category", index=True, ondelete="")
    parent_path = fields.Char(index=True, unaccent=False)

    child_ids = fields.One2many("ni.observation.category", "parent_id", index=True)

    type_ids = fields.One2many("ni.observation.type", "category_id")
    type_count = fields.Integer(compute="_compute_type_count", store=True)

    @api.depends("type_ids")
    def _compute_type_count(self):
        for rec in self:
            rec.type_count = len(rec.type_ids)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
