#  Copyright (c) 2021 NSTDA

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

LOCK_STATE_DICT = {
    "cancelled": [("readonly", True)],
    "entered-in-error": [("readonly", True)],
    "finished": [("readonly", True)],
}


class Encounter(models.Model):
    _name = "ni.encounter"
    _description = "Encounter"
    _inherit = ["mail.thread", "period.mixin", "image.mixin", "ir.sequence.mixin"]
    _check_company_auto = True
    _order = "name DESC"

    company_id = fields.Many2one(
        related="patient_id.company_id",
        index=True,
        store=True,
    )
    name = fields.Char(
        "Encounter No.",
        copy=False,
        states=LOCK_STATE_DICT,
        index=True,
        required=True,
        default=lambda self: self._sequence_default,
    )
    color = fields.Integer()
    class_id = fields.Many2one(
        "ni.encounter.cls",
        "Classification",
        index=True,
        required=True,
        states=LOCK_STATE_DICT,
        help="Classification of patient encounter",
        ondelete="restrict",
        tracking=True,
    )
    period_start = fields.Date(readonly=True, states={"draft": [("readonly", False)]})
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        readonly=True,
        required=True,
        ondelete="cascade",
        states={"draft": [("readonly", False)]},
        auto_join=True,
    )
    patient_gender = fields.Selection(related="patient_id.gender", store=True)
    patient_age = fields.Integer(related="patient_id.age", store=True)

    partner_id = fields.Many2one(
        related="patient_id.partner_id",
        string="Patient Contact",
        store=True,
        index=True,
    )
    image_1920 = fields.Image(related="patient_id.image_1920", readonly=False)
    image_1024 = fields.Image(related="patient_id.image_1024", readonly=False)
    image_512 = fields.Image(related="patient_id.image_512", readonly=False)
    image_256 = fields.Image(related="patient_id.image_256", readonly=False)
    image_128 = fields.Image(related="patient_id.image_128", readonly=False)

    priority = fields.Selection(
        [("0", "Routine"), ("1", "Urgent"), ("2", "ASAP"), ("3", "STAT")],
        default="0",
        tracking=True,
        states=LOCK_STATE_DICT,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("planned", "Planned"),
            ("cancelled", "Cancelled"),
            ("in-progress", "In-Progress"),
            ("finished", "Discharged"),
            ("entered-in-error", "Error Entry"),
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
        states=LOCK_STATE_DICT,
        tracking=True,
    )
    location_history_ids = fields.One2many(
        "ni.encounter.location.rel",
        "encounter_id",
        states=LOCK_STATE_DICT,
        copy=True,
    )
    location_history_count = fields.Integer(
        string="Location", compute="_compute_location_history_count", store=True
    )
    reason_ids = fields.Many2many(
        "ni.encounter.reason",
        "ni_encounter_reason_rel",
        "encounter_id",
        "reason_id",
        states=LOCK_STATE_DICT,
        copy=True,
        help="Reason the encounter takes place",
    )

    # Hospitalization
    hospitalization = fields.Boolean(related="class_id.hospitalization", store=True)
    pre_admit_identifier = fields.Char(
        states=LOCK_STATE_DICT, tracking=True, help="Pre-admission identifier"
    )
    origin_partner_id = fields.Many2one(
        "res.partner",
        string="Transfer from",
        states=LOCK_STATE_DICT,
        tracking=True,
        help="organization which the patient came before admission",
        copy=True,
    )
    admit_source_id = fields.Many2one(
        "ni.encounter.admit",
        "Admission Source",
        states=LOCK_STATE_DICT,
        tracking=True,
        help="From where patient was admitted (physician referral, transfer)",
    )
    re_admit = fields.Boolean(
        "Re-Admission",
        states=LOCK_STATE_DICT,
        tracking=True,
        help="The type of hospital re-admission that has occurred (if any). "
        "If the value is absent, then this is not identified as a readmission",
    )
    re_admit_reason = fields.Text(
        "Re-Admission Reason",
        states=LOCK_STATE_DICT,
        tracking=True,
    )
    diet_ids = fields.Many2many(
        "ni.encounter.diet",
        "ni_encounter_diet_rel",
        "encounter_id",
        "diet_id",
        string="Diet Preferences",
        states=LOCK_STATE_DICT,
    )
    arrangement_ids = fields.Many2many(
        "ni.encounter.arrangement",
        "ni_encounter_arrangement_rel",
        "encounter_id",
        "arrange_id",
        string="Special Arrangements",
        states=LOCK_STATE_DICT,
    )
    courtesy_ids = fields.Many2many(
        "ni.encounter.courtesy",
        "ni_encounter_courtesy_rel",
        "encouter_id",
        "courtesy_id",
        string="Special Courtesy",
        states=LOCK_STATE_DICT,
    )
    discharge_id = fields.Many2one(
        "ni.encounter.discharge",
        "Disposition",
        help="Category or kind of location after discharge",
        tracking=True,
    )
    discharge_partner_id = fields.Many2one(
        "res.partner",
        "Destination",
        domain="[('is_company', '=', True)]",
        help="Location/organization to which the patient is discharged",
        tracking=True,
    )
    discharge_note = fields.Text("Note", tracking=True)

    # Participant
    performer_id = fields.Many2one(
        "res.partner",
        "Primary Performer",
        tracking=True,
        states=LOCK_STATE_DICT,
        domain="[('is_company', '=', False)]",
    )
    performer_id_2 = fields.Many2one(
        "res.partner",
        "Secondary Performer",
        tracking=True,
        states=LOCK_STATE_DICT,
        domain="[('is_company', '=', False), ('id', '!=', performer_id)]",
    )
    attendant_ids = fields.Many2many(
        "res.partner",
        "ni_encounter_secondary_performer",
        "encounter_id",
        "partner_id",
        "Attendants",
        states=LOCK_STATE_DICT,
        domain="""[
            ('is_company', '=', False),
            ('id', 'not in', [performer_id, performer_id_2, consultant_id])
        ]""",
    )
    consultant_id = fields.Many2one(
        "res.partner",
        tracking=True,
        states=LOCK_STATE_DICT,
        domain="[('is_company', '=', False), ('id', '!=', performer_id)]",
    )
    workflow_event_ids = fields.One2many("ni.workflow.event", "encounter_id")
    workflow_request_ids = fields.One2many("ni.workflow.request", "encounter_id")

    _sql_constraints = [
        (
            "company_id__name__uniq",
            "unique (company_id, name)",
            "This Encounter No. already exists!",
        ),
    ]

    @api.depends("location_history_ids")
    def _compute_location_history_count(self):
        for rec in self:
            rec.location_history_count = len(rec.location_history_ids)

    @api.onchange("patient_id")
    def onchange_patient(self):
        if self.patient_id:
            encounter = self._get_another_active_encounter()
            if encounter:
                return {
                    "warning": {
                        "title": _("Warning!"),
                        "message": _(
                            "%s was already registered as Encounter No. %s (%s)."
                        )
                        % (
                            self.patient_id.name,
                            encounter.name,
                            encounter._get_state_label(),
                        ),
                    }
                }

            if self.patient_id.deceased:
                warning = {
                    "title": _("Warning!"),
                    "message": _(
                        "%s is already deceased. Reference to this patient may "
                        "cause database inconsistency!"
                    )
                    % self.patient_id.name,
                }
                return {"warning": warning}
            self.pre_admit_identifier = self.patient_id.code

    def _get_another_active_encounter(self):
        self.ensure_one()
        return (
            self.env["ni.encounter"]
            .sudo()
            .search(
                [
                    ("patient_id", "=", self.patient_id.id),
                    ("name", "!=", self.name),
                    ("state", "in", ["draft", "planned", "in-progress"]),
                ],
                order="id DESC",
                limit=1,
            )
        )

    def _get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    @api.constrains("performer_id", "performer_id_2")
    def _check_performer_id(self):
        for rec in self:
            if not rec.performer_id:
                continue
            if rec.performer_id == rec.performer_id_2:
                raise ValidationError(
                    _("Primary and Secondary performer should not be the same person")
                )

    @api.constrains(
        "consultant_id",
    )
    def _check_consultant_id(self):
        for rec in self:
            if not rec.consultant_id:
                continue
            if (
                rec.consultant_id == rec.performer_id
                or rec.consultant_id == rec.performer_id_2
            ):
                raise ValidationError(_("Consultant should not be performer"))

    def name_get(self):
        res = []
        for rec in self:
            name = rec._get_name()
            res.append((rec.id, name))
        return res

    def _get_name(self):
        self.ensure_one()
        rec = self
        name = rec.name
        if self._context.get("show_class"):
            name = "{}/{}".format(name, rec.class_id.code or rec.class_id.name)
        if self._context.get("show_patient") or self._context.get("show_patient_name"):
            name = "{}: {}".format(name, rec.patient_id.name)
        if self._context.get("show_state"):
            name = "{} [{}]".format(name, rec._get_state_label())
        if self._context.get("show_location") and rec.location_id:
            name = "{}\n{}".format(name, rec.location_id.display_name)
        return name

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if name:
            # Also search for patient name
            args = [
                "|",
                ("name", operator, name),
                ("patient_id", operator, name),
            ] + args
        location_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(location_ids).with_user(name_get_uid))

    @api.model
    def create(self, vals):
        result = super().create(vals)
        if result.location_id:
            result._create_location_hist(
                location=result.location_id.id, start=result.period_start
            )
        result.patient_id._compute_encounter()
        return result

    def write(self, vals):
        origin_location = self._origin.location_id
        new_location = vals.get("location_id")
        if new_location and not origin_location:
            self._create_location_hist(new_location, self.period_start)
        if (new_location and origin_location) and (new_location != origin_location):
            last_location = self.get_last_location()
            if last_location.period_start != fields.date.today():
                self._create_location_hist(new_location)
                last_location.update(
                    {"period_end": fields.date.today() - relativedelta(days=1)}
                )
            else:
                last_location.update({"location_id": new_location})

        res = super().write(vals)
        if "state" in vals:
            for enc in self:
                enc.patient_id._compute_encounter()
        return res

    def get_last_location(self):
        enc_location = self.env["ni.encounter.location.rel"].sudo()
        return enc_location.search(
            args=[("encounter_id", "=", self.id)], order="period_start DESC", limit=1
        )

    def _create_location_hist(self, location, start=None):
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
                raise ValidationError(
                    _("Verified encounter must defined start date (since)")
                )
            if enc.state == "draft":
                if today < enc.period_start:
                    enc.update({"state": "planned"})
                else:
                    enc.update({"state": "in-progress"})
            elif enc.state == "planned":
                enc.update(
                    {"state": "in-progress", "period_start": fields.Date.today()}
                )
            else:
                raise ValidationError(
                    _("Invalid State!, Please contact your system administrator")
                )

    def action_close(self):
        for enc in self:
            if enc.state != "in-progress":
                raise ValidationError(_("Must be in-progress state"))
            else:
                enc.update({"state": "finished", "period_end": fields.date.today()})

    def action_entered_in_error(self):
        self.write({"state": "entered-in-error"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancelled"})
