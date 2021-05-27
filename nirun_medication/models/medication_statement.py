#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class MedicationStatement(models.Model):
    _name = "ni.medication.statement"
    _description = "Medication Statement"
    _inherit = ["ni.patient.res", "period.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(related="medication_id.name", store=False)
    location_id = fields.Many2one(
        related="encounter_id.location_id", store=True, index=True,
    )
    category_id = fields.Many2one(
        "ni.medication.statement.category",
        "Statement Category",
        required=True,
        ondelete="restrict",
    )
    medication_id = fields.Many2one("ni.medication", required=True, ondelete="restrict")
    state = fields.Selection(
        [("active", "Currently"), ("completed", "Completed"), ("stopped", "Stopped")],
        default="active",
        required=True,
    )
    state_reason = fields.Char(required=False)
    period_start = fields.Date(required=True)
    active = fields.Boolean(default=True)

    reason_ref = fields.Reference(
        [("ni.patient.condition", "Condition"), ("ni.observation", "Observation")],
        required=False,
    )
    dosage = fields.Text(help="How the medication is/was taken or should be taken")
    dosage_timing = fields.Many2one(
        "ni.timing",
        "Timing",
        help="When medication should be administered",
        auto_join=True,
    )
    dosage_when = fields.Many2many(string="Dosage (when)", related="dosage_timing.when")
    dosage_as_need = fields.Boolean("As need?", default=False)

    def name_get(self):
        if self._context.get("show_since"):
            return [(rec.id, rec.name_since()) for rec in self]
        return [(rec.id, rec.name) for rec in self]

    def name_since(self):
        return "{} [{}]".format(self.name, self.period_start)
