#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class InsurancePlan(models.Model):
    _name = "ni.insurance.plan"
    _description = "Insurance Plan"
    _inherit = ["coding.base", "image.mixin"]
    _order = "sequence"

    name = fields.Char("Insurance Plan")
    display_name = fields.Char(compute="_compute_display_name")
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
            coverage_ids = coverage.filtered(lambda s: s.insurance_plan_id == rec)
            rec.patient_ids = coverage_ids.mapped("patient_id")
            rec.patient_count = len(rec.patient_ids)

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    @api.depends(
        "name",
        "issuer_id",
    )
    def _compute_display_name(self):
        diff = dict(show_issuer=True, show_alias=None, show_code=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    def _name_get(self):
        plan = self
        name = plan.name or ""
        if self._context.get("show_issuer") and plan.issuer_id:
            name = "{}, {}".format(plan.issuer_id.name, name)
        if self._context.get("show_alias") and plan.alias:
            name = "{} ({})".format(name, plan.alias)
        if self._context.get("show_code") and plan.code:
            name = "[{}] {}".format(plan.code, name)
        return name
