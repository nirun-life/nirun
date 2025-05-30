#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class CareplanCategory(models.Model):
    _name = "ni.careplan.category"
    _description = "Careplan Category"
    _inherit = ["ni.coding"]

    _parent_store = True

    parent_id = fields.Many2one("ni.careplan.category", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    condition_code_ids = fields.Many2many(
        "ni.condition.code", "ni_careplan_category_condition_code"
    )
    goal_category_id = fields.Many2one("ni.goal.category", help="Default goal category")
    goal_code_ids = fields.Many2many("ni.goal.code", "ni_careplan_category_goal_code")
    service_category_id = fields.Many2one(
        "ni.service.category", help="Default service category"
    )
    service_request_ids = fields.One2many("ni.careplan.template.service", "template_id")

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))


class ServiceTemplate(models.Model):
    _name = "ni.careplan.template.service"
    _inherit = "ni.timing.mixin"

    company_id = fields.Many2one("res.company", copy=False)
    template_id = fields.Many2one("ni.careplan.category", copy=False)
    name = fields.Char("Service Name", required=True)
    category_id = fields.Many2one(
        "ni.service.category",
        domain=lambda self: [
            ("id", "!=", self.env.ref("ni_service.categ_routine").id),
        ],
    )
    service_ids = fields.Many2many(
        "ni.service",
        "ni_careplan_template_service_rel",
        "template_id",
        "service_id",
        check_company=True,
    )

    def _default_service_domain(self):
        return [("category_id", "!=", self.env.ref("ni_service.categ_routine").id)]

    @api.onchange("category_id")
    def _onchange_category_id(self):
        if self.category_id:
            domain = [("category_id", "=", self.category_id.id)]
        else:
            domain = self._default_service_domain()
        return {"domain": {"service_ids": domain}}

    @api.onchange("service_ids")
    def _onchange_service_ids(self):
        for rec in self:
            if rec.service_ids:
                rec.name = ", ".join(rec.service_ids.mapped("name"))
