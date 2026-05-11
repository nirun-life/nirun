#  Copyright (c) 2026 NSTDA
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ImmunizationEvaluationWizard(models.TransientModel):
    _name = "ni.immunization.evaluation.wizard"
    _description = "Immunization Evaluation Wizard"

    encounter_id = fields.Many2one("ni.encounter", required=True)
    patient_id = fields.Many2one(related="encounter_id.patient_id")
    state = fields.Selection(
        [("1", "Disease"), ("2", "Dose")], default="1", required=True
    )
    disease_ids = fields.Many2many("ni.immunization.target.disease", string="Diseases")
    line_ids = fields.One2many(
        "ni.immunization.evaluation.wizard.line", "wizard_id", string="Doses"
    )

    def action_next(self):
        self.ensure_one()
        if not self.disease_ids:
            raise ValidationError(_("Please select at least one disease."))
        Evaluation = self.env["ni.immunization.evaluation"]
        lines = []
        for disease in self.disease_ids:
            prior_count = Evaluation.search_count(
                [
                    ("patient_id", "=", self.patient_id.id),
                    ("target_disease_id", "=", disease.id),
                ]
            )
            lines.append(
                fields.Command.create(
                    {
                        "target_disease_id": disease.id,
                        "dose_number": prior_count + 1,
                        "series_doses": disease.series_doses,
                        "occurrence": fields.Date.today(),
                    }
                )
            )
        self.write({"line_ids": lines, "state": "2"})
        return self._reopen()

    def action_back(self):
        self.ensure_one()
        self.line_ids.unlink()
        self.state = "1"
        return self._reopen()

    def action_apply(self):
        self.ensure_one()
        Evaluation = self.env["ni.immunization.evaluation"]
        for line in self.line_ids:
            Evaluation.create(
                {
                    "encounter_id": self.encounter_id.id,
                    "patient_id": self.patient_id.id,
                    "target_disease_id": line.target_disease_id.id,
                    "dose_number": line.dose_number,
                    "series_doses": line.series_doses,
                    "occurrence": line.occurrence,
                }
            )

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }


class ImmunizationEvaluationWizardLine(models.TransientModel):
    _name = "ni.immunization.evaluation.wizard.line"
    _description = "Immunization Evaluation Wizard Line"

    wizard_id = fields.Many2one(
        "ni.immunization.evaluation.wizard", required=True, ondelete="cascade"
    )
    target_disease_id = fields.Many2one(
        "ni.immunization.target.disease", string="Disease", required=True, readonly=True
    )
    dose_number = fields.Integer("Dose #", required=True, default=1)
    series_doses = fields.Integer("Required", required=True, default=1)
    occurrence = fields.Date("Last Occurred", required=True, default=fields.Date.today)
