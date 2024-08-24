#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models


class MedicationSuggestWizard(models.Model):
    _name = "ni.medication.suggest.wizard"
    _description = "Medication Suggestion Wizard"

    @api.model
    def default_get(self, fields):
        res = super(MedicationSuggestWizard, self).default_get(fields)
        if "reason_id" in fields and "reason_id" not in res and res.get("encounter_id"):
            reason = self.env["ni.encounter"].browse(res["encounter_id"]).reason_ids
            if reason:
                res["reason_id"] = reason[0].id
        return res

    encounter_id = fields.Many2one("ni.encounter", required=True)
    reason_ids = fields.Many2many(related="encounter_id.reason_ids")
    reason_id = fields.Many2one(
        "ni.encounter.reason", domain="[('id', 'in', reason_ids)]"
    )
    suggest_id = fields.Many2one("ni.medication.suggest", required=True)
    suggest_line_ids = fields.One2many(related="suggest_id.line_ids")
    suggest_line_count = fields.Integer(related="suggest_id.line_count")
    occurrence = fields.Datetime("Handed Over", default=fields.Datetime.now())

    def action_apply(self):
        self.ensure_one()
        self.encounter_id.update(
            {
                "medication_dispense_ids": [
                    fields.Command.create(self._prepare_dispense(m))
                    for m in self.suggest_line_ids
                ]
            }
        )

    def _prepare_dispense(self, suggest_line):
        data = suggest_line.copy_data(
            {
                "encounter_id": self.encounter_id.id,
                "patient_id": self.encounter_id.patient_id.id,
                "occurrence": self.occurrence,
            }
        )[0]
        field = self.env["ni.medication.dispense"]._fields
        return {k: v for k, v in data.items() if k in field}
