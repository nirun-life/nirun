#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class InsurancePlan(models.Model):
    _name = "ni.insurance.plan"
    _description = "Insurance Plan"
    _inherit = ["ni.coding", "image.mixin"]
    _order = "sequence"

    name = fields.Char("Insurance Plan")
    alias = fields.Char()
    type_id = fields.Many2one("ni.coverage.type", required=True)
    issuer_id = fields.Many2one("res.partner", domain=[("is_company", "=", True)])
    benefit_ids = fields.One2many(
        "ni.insurance.plan.benefit",
        "plan_id",
        "Cost to Beneficiary",
        help="Plan payments for services/products",
    )

    coverage_ids = fields.One2many(
        "ni.coverage",
        "insurance_plan_id",
        "Coverages",
        domain=[("state", "=", "active")],
    )
    patient_ids = fields.Many2many("ni.patient", compute="_compute_patient")
    patient_count = fields.Integer(compute="_compute_patient")

    @api.depends("coverage_ids", "coverage_ids.state")
    def _compute_patient(self):
        coverage = self.env["ni.coverage"].search(
            [("insurance_plan_id", "in", self.ids), ("state", "=", "active")]
        )
        for rec in self:
            coverage_ids = coverage.filtered(
                lambda s, plan=rec: s.insurance_plan_id == plan
            )
            rec.patient_ids = coverage_ids.mapped("patient_id")
            rec.patient_count = len(rec.patient_ids)

    @api.depends("issuer_id.name", "alias")
    @api.depends_context("show_issuer", "show_alias")
    def _compute_display_name(self):
        for plan in self:
            plan.display_name = plan._name_get()

    def _name_get(self):
        plan = self
        context = self.env.context
        name = plan.name or ""
        if context.get("show_issuer", True) and plan.issuer_id:
            name = f"{plan.issuer_id.name}, {name}"
        if context.get("show_alias") and plan.alias:
            name = f"{name} ({plan.alias})"
        if context.get("show_code") and plan.code:
            name = f"[{plan.code}] {name}"
        return name
