#  Copyright (c) 2021 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Encounter(models.Model):
    _name = "ni.encounter"
    _description = "Encounter"
    _inherit = ["mail.thread", "period.mixin", "image.mixin", "ir.sequence.mixin"]
    _check_company_auto = True
    _order = "name DESC"

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
    )
    name = fields.Char(
        "Identifier",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        index=True,
        default=lambda self: self._sequence_default,
    )
    class_id = fields.Many2one(
        "ni.encounter.cls",
        "Classification",
        index=True,
        required=True,
        help="Classification of patient encounter",
        ondelete="restrict",
        tracking=True,
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        readonly=True,
        required=True,
        ondelete="cascade",
        states={"draft": [("readonly", False)]},
        auto_join=True,
    )
    partner_id = fields.Many2one(
        related="patient_id.partner_id", store=True, index=True
    )
    image_1920 = fields.Image(related="patient_id.image_1920")
    image_1024 = fields.Image(related="patient_id.image_1024")
    image_512 = fields.Image(related="patient_id.image_512")
    image_256 = fields.Image(related="patient_id.image_256")
    image_128 = fields.Image(related="patient_id.image_128")

    priority = fields.Selection(
        [("0", "Routine"), ("1", "Urgent"), ("2", "ASAP"), ("3", "STAT")], tracking=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("planned", "Planned"),
            ("in-progress", "Progressing"),
            ("finished", "Finished"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        default="draft",
    )
    location_id = fields.Many2one(
        "ni.location",
        "Location",
        help="Where services are provided to the patient",
        tracking=True,
    )
    location_history_ids = fields.One2many(
        "ni.encounter.location.rel",
        "encounter_id",
        states={"cancelled": [("readonly", True)], "finished": [("readonly", True)]},
        copy=True,
    )

    reason_ids = fields.Many2many(
        "ni.encounter.reason",
        "ni_encounter_reason_rel",
        "encounter_id",
        "reason_id",
        copy=True,
        help="Reason the encounter takes place",
    )

    condition_id = fields.One2many(
        "ni.patient.condition",
        "encounter_id",
        states={"cancelled": [("readonly", True)], "finished": [("readonly", True)]},
    )

    # Hospitalization
    origin_partner_id = fields.Many2one(
        "res.partner",
        string="Transfer from",
        domain=[("is_company", "=", True)],
        help="The organization from which the patient came before admission",
        copy=True,
    )
    admit_id = fields.Many2one(
        "ni.encounter.admit",
        "Admit Source",
        help="From where patient was admitted (physician referral, transfer)",
    )
    re_admission = fields.Boolean(
        "Re-Admission",
        help="The type of hospital re-admission that has occurred (if any). "
        "If the value is absent, then this is not identified as a readmission",
    )
    diet_ids = fields.Many2many(
        "ni.encounter.diet",
        "ni_encounter_diet_rel",
        "encounter_id",
        "diet_id",
        "Diet Preferences",
    )
    arrangement_ids = fields.Many2many(
        "ni.encounter.arrangement",
        "ni_encounter_arrangement_rel",
        "encounter_id",
        "arrange_id",
        "Special Arrangements",
    )
    courtesy_ids = fields.Many2many(
        "ni.encounter.courtesy",
        "ni_encounter_courtesy_rel",
        "encouter_id",
        "courtesy_id",
        "Special Courtesy",
    )
    discharge_id = fields.Many2one(
        "ni.encounter.discharge",
        "Disposition",
        help="Category or kind of location after discharge",
    )
    discharge_partner_id = fields.Many2one(
        "res.partner",
        "Refer to",
        domain="[('is_company', '=', True)]",
        help="Location/organization to which the patient is discharged",
    )

    _sql_constraints = [
        (
            "company_id__name__uniq",
            "unique (company_id, name)",
            "Name already exists !",
        ),
    ]

    def name_get(self):
        if self._context.get("show_patient_name"):
            return [
                (en.id, "{} [{}]".format(en.name, en.patient_id.name)) for en in self
            ]
        if self._context.get("show_state"):
            state = dict(self._fields["state"].selection)
            return [
                (en.id, "{} [{}]".format(en.name, state.get(en.state))) for en in self
            ]
        return super(Encounter, self).name_get()

    @api.model
    def create(self, vals):
        result = super().create(vals)
        if result.location_id:
            result._create_location_hist(
                location=result.location_id.id, start=result.period_start
            )
        return result

    def write(self, vals):
        origin_location = self._origin.location_id
        new_location = vals.get("location_id")
        if new_location and not origin_location:
            self._create_location_hist(new_location, self.period_start)
        if (new_location and origin_location) and (new_location != origin_location):
            last_location = self._get_last_location()
            if last_location.period_start != fields.date.today():
                self._create_location_hist(new_location)
                last_location.update(
                    {"period_end": fields.date.today() - relativedelta(days=1)}
                )
            else:
                last_location.update({"location_id": new_location})
        super().write(vals)

    def _get_last_location(self):
        enc_location = self.env["ni.encounter.location.rel"].sudo()
        return enc_location.search(
            args=[("encounter_id", "=", self.id)], order="period_start DESC", limit=1
        )

    def _create_location_hist(self, location, start):
        self.ensure_one()
        encounter_location = self.env["ni.encounter.location.rel"].sudo()
        encounter_location.create(
            {
                "company_id": self.company_id.id,
                "encounter_id": self.id,
                "location_id": location,
                "period_start": start or fields.date.today(),
            }
        )

    def action_confirm(self):
        today = fields.date.today()
        for enc in self:
            if not enc.period_start:
                raise UserError(_("Verified encounter must defined start date (since)"))
            if today < enc.period_start:
                enc.update({"state": "planned"})
            else:
                enc.update({"state": "in-progress"})

    def action_close(self):
        for enc in self:
            if enc.state != "in-progress":
                raise UserError(_("Must be in-progress state"))
            else:
                enc.update({"state": "finished", "period_end": fields.date.today()})
