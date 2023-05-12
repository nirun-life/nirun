#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    medication_statement_ids = fields.One2many(
        "ni.medication.statement",
        "patient_id",
        string="Medication Statements",
        check_company=True,
        groups="ni_medication.group_user",
    )
    medication_statement_count = fields.Integer(compute="_compute_medication_count")

    def _compute_medication_count(self):
        statement = self.env["ni.medication.statement"].sudo()
        read = statement.read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["patient_id"]
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in read}
        for patient in self:
            patient.medication_statement_count = data.get(patient.id, 0)

    def action_medication_statement(self, target=None):
        action_rec = self.env.ref("ni_medication.ni_medication_statement_action")
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
        if target:
            action["target"] = target
        return action
