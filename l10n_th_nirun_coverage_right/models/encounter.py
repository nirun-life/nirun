#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    coverage_plan_id = fields.Many2one(
        "ni.insurance.plan",
        tracking=True,
        ondelete="set null",
        help="coverage (Insurance) plan for this encounter",
    )
    coverage_partner_id = fields.Many2one(
        "res.partner",
        "Coverage Network",
        tracking=True,
        ondelete="set null",
        help="Organization that provide health coverage",
    )

    @api.model
    def create(self, vals):
        return super(Encounter, self).create(vals)._write_coverage_plan_to_patient()

    def write(self, vals):
        res = super(Encounter, self).write(vals)
        self._write_coverage_plan_to_patient()
        return res

    def _write_coverage_plan_to_patient(self):
        for rec in self:
            patient = rec.patient_id
            if rec.coverage_plan_id and not patient.coverage_plan_id:
                patient.write(
                    {
                        "coverage_plan_id": rec.coverage_plan_id.id,
                        "coverage_partner_id": rec.coverage_partner_id.id,
                    }
                )
        return self

    @api.onchange("patient_id")
    def onchange_patient(self):
        super(Encounter, self).onchange_patient()
        if self.patient_id and self.patient_id.coverage_plan_id:
            self.update(
                {
                    "coverage_plan_id": self.patient_id.coverage_plan_id.id,
                    "coverage_partner_id": self.patient_id.coverage_partner_id.id,
                }
            )
