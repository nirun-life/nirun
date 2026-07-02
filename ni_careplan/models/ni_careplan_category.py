#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class CareplanCategory(models.Model):
    _name = "ni.careplan.category"
    _description = "Careplan Category"
    _inherit = ["ni.coding"]

    _parent_store = True

    def _default_company_id(self):
        if self.env.user.has_group("ni_patient.group_admin"):
            return False
        return self.env.company.id

    company_id = fields.Many2one(
        "res.company", required=False, index=True, default=_default_company_id
    )
    opted_company_ids = fields.Many2many(
        "res.company",
        "res_company_careplan_category",
        "category_id",
        "company_id",
        string="Opted-in Companies",
        help="Companies that enabled this shared category via their own careplan configuration.",
    )
    parent_id = fields.Many2one("ni.careplan.category", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    goal_category_id = fields.Many2one("ni.goal.category", help="Default goal category")
    service_category_id = fields.Many2one(
        "ni.service.category", help="Default service category"
    )
    template_ids = fields.One2many("ni.careplan.template", "category_id")

    observation_category_ids = fields.Many2many(
        "ni.observation.category",
        help="If this empty it mean careplan not address observation",
    )
    observation_category_count = fields.Integer(
        compute="_compute_observation_category_count"
    )
    observation_code_ids = fields.Many2many(
        "ni.observation.type",
        domain="[('category_id', 'in', observation_category_ids)]",
        help="Leave this empty if apply to all type of selected categories",
    )

    @api.depends("observation_category_ids")
    def _compute_observation_category_count(self):
        for rec in self:
            rec.observation_category_count = len(rec.observation_category_ids)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
