#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    medication_ids = fields.One2many(
        "ni.medication.statement",
        "patient_id",
        string="Medication Statements",
        domain=[("state", "=", "active")],
    )
    medication_count = fields.Integer(compute="_compute_medication_count")

    @api.depends("medication_ids")
    def _compute_medication_count(self):
        for rec in self:
            rec.medication_count = len(rec.medication_ids)

    def action_medication_statement(self):
        action_rec = self.env.ref("nirun_medication.medication_statement_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.ids[0],
                "search_default_period_today": True,
                "default_patient_id": self.ids[0],
            }
        )
        action["context"] = ctx
        return action
