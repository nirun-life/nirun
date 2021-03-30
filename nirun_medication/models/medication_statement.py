#  Copyright (c) 2021 Piruin P.
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class MedicationStatement(models.Model):
    _name = "ni.medication.statement"
    _description = "Medication Statement"
    _inherit = ["ni.patient.res", "period.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(related="medication_id.name", store=False)
    location_id = fields.Many2one(
        related="encounter_id.location_id", store=True, index=True
    )
    category_id = fields.Many2one("ni.medication.statement.category", required=True)
    medication_id = fields.Many2one("ni.medication", required=True)
    state = fields.Selection(
        [("active", "Active"), ("completed", "Completed"), ("stopped", "Stopped")],
        default="active",
        required=True,
    )
    state_reason = fields.Char(required=False)
    period_start = fields.Date(string="Since", required=True)
    period_end = fields.Date(string="Until")
    period_end_calendar = fields.Date(compute="_compute_period_end_calendar")
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
    dosage_when = fields.Many2many(related="dosage_timing.when")
    dosage_as_need = fields.Boolean("As need?", help='Take "as needed"', default=False)

    def name_get(self):
        if self._context.get("show_since"):
            return [(rec.id, rec.name_since()) for rec in self]
        return [(rec.id, rec.name) for rec in self]

    def name_since(self):
        return "{} [{}]".format(self.name, self.period_start)

    @api.depends("period_start", "period_end")
    def _compute_period_end_calendar(self):
        for rec in self:
            # adding 1 days because calendar view's date_stop is exclusive date
            rec.period_end_calendar = (
                rec.period_end or fields.Date.context_today(self)
            ) + relativedelta(days=1)
