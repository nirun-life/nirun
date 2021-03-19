#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class MedicationStatement(models.Model):
    _name = "ni.medication.statement"
    _description = "Medication Statement"
    _inherit = ["ni.patient.res", "period.mixin", "mail.thread", "mail.activity.mixin"]

    category_id = fields.Many2one("ni.medication.statement.category", required=True)
    medication_id = fields.Many2one("ni.medication", required=True)
    state = fields.Selection(
        [("active", "Active"), ("completed", "Completed"), ("stopped", "Stopped")],
        default="active",
    )
    period_start = fields.Date(required=True)
    active = fields.Boolean(default=True)
    state_reason = fields.Char(required=False)
    reason_ref = fields.Reference(
        [("ni.patient.condition", "Condition"), ("ni.observation", "Observation")],
        required=False,
    )
    dosage = fields.Text()
