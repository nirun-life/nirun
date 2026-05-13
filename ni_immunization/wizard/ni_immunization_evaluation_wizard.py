#  Copyright (c) 2026 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ImmunizationEvaluationWizard(models.TransientModel):
    _name = "ni.immunization.evaluation.wizard"
    _description = "Immunization Evaluation Wizard"

    encounter_id = fields.Many2one("ni.encounter", required=True)
    patient_id = fields.Many2one(related="encounter_id.patient_id")
    immunization_id = fields.Many2one("ni.immunization", ondelete="cascade")
    state = fields.Selection(
        [("1", "Disease"), ("2", "Dose")], default="1", required=True
    )
    filter_status = fields.Selection(
        [
            ("all", "All"),
            ("not-protected", "Not Protected"),
            ("protected", "Protected"),
        ],
        default="all",
        required=True,
        string="Show",
    )
    available_disease_ids = fields.Many2many(
        "ni.immunization.target.disease",
        compute="_compute_available_disease_ids",
    )
    disease_ids = fields.Many2many(
        "ni.immunization.target.disease",
        "ni_immunization_evaluation_wizard_disease",
        "wizard_id",
        "disease_id",
        string="Diseases",
    )
    line_ids = fields.One2many(
        "ni.immunization.evaluation.wizard.line", "wizard_id", string="Doses"
    )

    @api.depends("patient_id", "filter_status")
    def _compute_available_disease_ids(self):
        Disease = self.env["ni.immunization.target.disease"]
        Summary = self.env["ni.immunization.summary"]
        all_diseases = Disease.search([])
        for wiz in self:
            if wiz.filter_status == "all" or not wiz.patient_id:
                wiz.available_disease_ids = all_diseases
                continue
            protected_ids = set(
                Summary.search(
                    [
                        ("patient_id", "=", wiz.patient_id.id),
                        ("protection_status", "=", "protected"),
                    ]
                )
                .mapped("target_disease_id")
                .ids
            )
            if wiz.filter_status == "protected":
                wiz.available_disease_ids = Disease.browse(protected_ids)
            else:
                wiz.available_disease_ids = all_diseases.filtered(
                    lambda d: d.id not in protected_ids
                )

    @api.onchange("filter_status")
    def _onchange_filter_status(self):
        self.disease_ids = False

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
            dose_number = prior_count + 1 if prior_count else disease.series_doses
            lines.append(
                fields.Command.create(
                    {
                        "target_disease_id": disease.id,
                        "dose_number": dose_number,
                        "series_doses": disease.series_doses,
                        "occurrence": False,
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
            vals = {
                "encounter_id": self.encounter_id.id,
                "patient_id": self.patient_id.id,
                "target_disease_id": line.target_disease_id.id,
                "dose_number": line.dose_number,
                "series_doses": line.series_doses,
                "immunization_date": line.occurrence,
            }
            if self.immunization_id:
                vals["immunization_id"] = self.immunization_id.id
            Evaluation.create(vals)

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
    occurrence = fields.Date(
        "Last Occurred",
    )
