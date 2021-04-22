#  Copyright (c) 2021 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Encounter(models.Model):
    _name = "ni.encounter"
    _description = _("Encounter with Patient")
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
    )
    name = fields.Char(
        "Identifier",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        index=True,
        default=lambda self: self._sequence_default,
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
    image_1920 = fields.Image(related="patient_id.image_1920")
    image_1024 = fields.Image(related="patient_id.image_1024")
    image_512 = fields.Image(related="patient_id.image_512")
    image_256 = fields.Image(related="patient_id.image_256")
    image_128 = fields.Image(related="patient_id.image_128")

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
    episode_ids = fields.One2many(
        "ni.care.episode",
        "encounter_id",
        states={"cancelled": [("readonly", True)], "finished": [("readonly", True)]},
        copy=True,
        auto_join=True,
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
    )
    origin_partner_id = fields.Many2one(
        "res.partner",
        string="From",
        domain=[("is_company", "=", True)],
        help="",
        copy=True,
    )
    condition_id = fields.One2many(
        "ni.patient.condition",
        "encounter_id",
        states={"cancelled": [("readonly", True)], "finished": [("readonly", True)]},
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

    @api.depends("episode_ids.period_start")
    def _compute_start(self):
        for encounter in self:
            if encounter.episode_ids:
                dates = encounter.episode_ids.mapped("period_start")
                encounter.period_start = min(dates)

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
            self._create_location_hist(location=new_location, start=self.period_start)
        elif (new_location and origin_location) and (
            new_location != self._origin.location_id
        ):
            encounter_location = self.env["ni.encounter.location.rel"].sudo()
            last_hist = encounter_location.search(
                [("encounter_id", "=", self.id)], order="period_start DESC", limit=1
            )
            if last_hist.period_start != fields.date.today():
                self._create_location_hist(location=new_location)
                last_hist.update(
                    {"period_end": fields.date.today() - relativedelta(days=1)}
                )
            else:
                last_hist.update({"location_id": new_location})
        super().write(vals)

    def _create_location_hist(self, location, start=lambda self: fields.date.today()):
        self.ensure_one()
        encounter_location = self.env["ni.encounter.location.rel"].sudo()
        encounter_location.create(
            {
                "company_id": self.company_id.id,
                "encounter_id": self.id,
                "location_id": location,
                "period_start": start,
            }
        )

    def action_confirm(self):
        today = fields.date.today()
        for enc in self:
            if not enc.period_start:
                raise UserError(
                    _(
                        "Verified encounter must defined episode "
                        + "of care period_start date"
                    )
                )
            if today < enc.period_start:
                enc.update({"state": "planned"})
            else:
                enc.update({"state": "in-progress"})

    def action_close(self):
        for enc in self:
            if enc.state != "in-progress":
                raise UserError(_("Must be in-progress state"))
            else:
                enc.update({"state": "finished"})
