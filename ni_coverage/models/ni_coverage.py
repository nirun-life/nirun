#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class Coverage(models.Model):
    _name = "ni.coverage"
    _description = "Coverage"
    _inherit = ["ni.period.mixin", "ni.identifier.mixin"]
    _order = "sequence"

    sequence = fields.Integer(index=True, default=0)
    name = fields.Char("Coverage Name", required=True, index=True)
    type_id = fields.Many2one("ni.coverage.type", index=True)
    kind = fields.Selection(related="type_id.kind", store=True, index=True)
    insurance_plan_id = fields.Many2one("ni.insurance.plan", index=True)
    insurance_plan_cost_ids = fields.One2many(
        string="Plan Benefit", related="insurance_plan_id.benefit_ids"
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        store=True,
        index=True,
        ondelete="cascade",
        required=True,
        check_company=True,
        help="Plan beneficiary",
    )
    beneficiary_id = fields.Many2one(
        "res.partner", "Beneficiary", related="patient_id.partner_id"
    )
    dependent_no = fields.Char("Dependent No.")
    subscriber_id = fields.Many2one("res.partner")
    subscriber_no = fields.Char("Subscriber No.")
    payor_ids = fields.Many2many(
        "res.partner", "ni_coverage_payor", "coverage_id", "payor_id"
    )
    policy_holder_id = fields.Many2one("res.partner", help="Owner of the policy")
    insurer = fields.Many2one("res.partner", domain=[("is_company", "=", True)])

    period_start = fields.Date(default=None)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("cancelled", "Cancelled"),
            ("entered-in-error", "Error Entry"),
        ],
        string="Status",
        default="draft",
        copy=False,
        index=True,
    )
    benefit_ids = fields.One2many(
        "ni.coverage.benefit",
        "coverage_id",
        "Cost to Beneficiary",
        help="Patient payments for services/products",
    )

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        coverage = self
        name = coverage.name or ""
        if self._context.get("show_patient"):
            name = "{}, {}".format(coverage.patient_id._name_get(), name)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, coverage.get_state_label())
        return name

    @api.onchange("insurance_plan_id")
    def _onchange_plan_id(self):
        for rec in self:
            if rec.insurance_plan_id:
                rec.name = rec.insurance_plan_id.name
                rec.type_id = rec.insurance_plan_id.type_id
                rec.beneficiary_id = rec.insurance_plan_id.benefit_ids.copy()

    def get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)
