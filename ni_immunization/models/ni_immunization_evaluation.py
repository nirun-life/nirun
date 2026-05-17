#  Copyright (c) 2026 NSTDA
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError


class ImmunizationEvaluation(models.Model):
    _name = "ni.immunization.evaluation"
    _description = "Immunization Evaluation"
    _inherit = ["ni.workflow.event.mixin", "ni.identifier.mixin"]
    _check_period_start = False
    _order = "occurrence DESC"
    _rec_name = "name"
    _identifier_ts_field = "occurrence"

    name = fields.Char(compute="_compute_name", store=True)
    state = fields.Selection(default="completed")
    occurrence = fields.Datetime("Asserted On")
    occurrence_date = fields.Datetime("Assert Date")

    immunization_date = fields.Date("Immunization Date")
    immunization_id = fields.Many2one(
        "ni.immunization",
        "Immunization Dose",
        ondelete="set null",
        domain="[('patient_id', '=?', patient_id)]",
    )
    target_disease_id = fields.Many2one(
        "ni.immunization.target.disease",
        "Target Disease",
        required=True,
        index=True,
        group_expand="_read_group_target_disease_ids",
    )
    target_disease_vaccine_ids = fields.Many2many(
        related="target_disease_id.vaccine_ids"
    )
    target_disease_definition = fields.Text(related="target_disease_id.definition")
    dose_status = fields.Selection(
        [("valid", "Valid"), ("not-valid", "Not Valid")],
        required=True,
        default="valid",
    )
    dose_status_reason = fields.Char(
        "Reason", help="Reason why the doses is considered invalid"
    )
    series = fields.Char(help="Name of the vaccine series")
    dose_number = fields.Integer("Dose #", default=1, group_operator="max")
    series_doses = fields.Integer("Doses Required", default=1, group_operator="max")
    protection_status = fields.Selection(
        [
            ("protected", "Protected"),
            ("partial", "Partial"),
            ("not-protected", "Not Protected"),
        ],
        compute="_compute_protection_status",
        store=True,
    )
    note = fields.Text()
    vaccine_target_disease_ids = fields.Many2many(
        "ni.immunization.target.disease",
        compute="_compute_vaccine_target_disease_ids",
    )
    history_ids = fields.Many2many(
        "ni.immunization.evaluation",
        compute="_compute_history_ids",
        string="History",
    )

    def init(self):
        self.env.cr.execute(
            """
            CREATE INDEX IF NOT EXISTS ni_immunization_evaluation_company_disease_idx
            ON ni_immunization_evaluation (company_id, patient_id, target_disease_id, occurrence DESC)
            """
        )
        self.env.cr.execute(
            """
            CREATE INDEX IF NOT EXISTS ni_immunization_evaluation_encounter_idx
            ON ni_immunization_evaluation (company_id, encounter_id)
            WHERE encounter_id IS NOT NULL
            """
        )

    @property
    def _workflow_name(self):
        return self.target_disease_id.display_name or self._description

    @property
    def _workflow_summary(self):
        parts = []
        if self.immunization_id:
            parts.append(self.immunization_id.name)
        if self.dose_number and self.series_doses:
            parts.append(f"Dose {self.dose_number}/{self.series_doses}")
        if self.protection_status:
            label = self.fields_get(["protection_status"])["protection_status"][
                "selection"
            ]
            parts.append(dict(label).get(self.protection_status, ""))
        return " · ".join(filter(None, parts))

    @api.depends("immunization_id.vaccine_id.target_disease_ids")
    def _compute_vaccine_target_disease_ids(self):
        for rec in self:
            rec.vaccine_target_disease_ids = (
                rec.immunization_id.vaccine_id.target_disease_ids
            )

    @api.model
    def _read_group_target_disease_ids(self, diseases, domain, order):
        disease_ids = diseases._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return diseases.browse(disease_ids)

    @api.depends("target_disease_id", "dose_number")
    def _compute_name(self):
        for rec in self:
            disease = rec.target_disease_id.display_name or ""
            dose = f"{rec.dose_number}"
            rec.name = f"{disease} #{dose}"

    @api.depends("patient_id", "target_disease_id")
    def _compute_history_ids(self):
        for rec in self:
            rec.history_ids = self.search(
                [
                    ("patient_id", "=", rec.patient_id.id),
                    ("target_disease_id", "=", rec.target_disease_id.id),
                    ("id", "!=", rec._origin.id),
                ]
            )

    @api.depends("dose_status", "dose_number", "series_doses")
    def _compute_protection_status(self):
        for rec in self:
            if rec.dose_status != "valid":
                rec.protection_status = "not-protected"
            elif rec.series_doses and rec.dose_number >= rec.series_doses:
                rec.protection_status = "protected"
            else:
                rec.protection_status = "partial"

    @api.constrains("immunization_id", "patient_id", "target_disease_id")
    def _check_immunization_id(self):
        for rec in self.filtered("immunization_id"):
            if rec.immunization_id.patient_id != rec.patient_id:
                raise ValidationError(
                    _(
                        "The referenced immunization dose belongs to a different patient."
                    )
                )
            vaccine_diseases = rec.immunization_id.vaccine_id.target_disease_ids
            if vaccine_diseases and rec.target_disease_id not in vaccine_diseases:
                raise ValidationError(
                    _(
                        "The vaccine '%(vaccine)s' does not target '%(disease)s'.",
                        vaccine=rec.immunization_id.vaccine_id.display_name,
                        disease=rec.target_disease_id.display_name,
                    )
                )
            duplicate = self.search(
                [
                    ("immunization_id", "=", rec.immunization_id.id),
                    ("target_disease_id", "=", rec.target_disease_id.id),
                    ("id", "!=", rec.id),
                ],
                limit=1,
            )
            if duplicate:
                raise ValidationError(
                    _(
                        "An evaluation for '%(disease)s' already references this immunization dose.",
                        disease=rec.target_disease_id.display_name,
                    )
                )

    @api.constrains("patient_id", "target_disease_id", "dose_number", "dose_status")
    def _check_unique_valid_dose(self):
        for rec in self:
            if rec.dose_status != "valid":
                continue
            duplicate = self.search(
                [
                    ("patient_id", "=", rec.patient_id.id),
                    ("target_disease_id", "=", rec.target_disease_id.id),
                    ("dose_number", "=", rec.dose_number),
                    ("dose_status", "=", "valid"),
                    ("id", "!=", rec.id),
                ],
                limit=1,
            )
            if duplicate:
                raise ValidationError(
                    f"A valid dose #{rec.dose_number} already exists for "
                    f"{rec.target_disease_id.display_name} on this patient."
                )

    @api.onchange("target_disease_id", "patient_id")
    def _onchange_target_disease_id(self):
        for rec in self:
            if rec.target_disease_id:
                rec.series_doses = rec.target_disease_id.series_doses
                prior_count = self.search_count(
                    [
                        ("patient_id", "=", rec.patient_id.id),
                        ("target_disease_id", "=", rec.target_disease_id.id),
                        ("id", "!=", rec._origin.id),
                    ]
                )
                rec.dose_number = prior_count + 1

    @api.onchange("immunization_id")
    def _onchange_immunization_id(self):
        for rec in self:
            if rec.immunization_id:
                rec.patient_id = rec.immunization_id.patient_id
                rec.encounter_id = rec.immunization_id.encounter_id
                rec.immunization_date = (
                    rec.immunization_id.occurrence.date()
                    if rec.immunization_id.occurrence
                    else False
                )
                diseases = rec.immunization_id.vaccine_id.target_disease_ids
                if len(diseases) == 1:
                    rec.target_disease_id = diseases
