#  Copyright (c) 2023 NSTDA
from odoo import _, api, fields, models


class CompanyType(models.Model):
    _name = "res.company.type"
    _inherit = "ni.coding"
    _description = "Organization Type"
    _parent_store = True

    parent_id = fields.Many2one("res.company.type", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    company_ids = fields.One2many("res.company", "type_id")
    company_count = fields.Integer(compute="_compute_company_count", store=True)

    @api.depends("company_ids")
    def _compute_company_count(self):
        for rec in self:
            rec.company_count = len(rec.company_ids)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
