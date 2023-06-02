#  Copyright (c) 2021-2023 NSTDA

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

LOCK_STATE_DICT = {
    "cancelled": [("readonly", True)],
    "entered-in-error": [("readonly", True)],
    "finished": [("readonly", True)],
}

SIGN_FILEDS = [
    "chief_complaint",
    "hist_of_present_illness",
    "review_of_systems",
    "physical_exam",
]


class Encounter(models.Model):
    _name = "ni.encounter"
    _description = "Encounter"
    _inherit = ["mail.thread", "ni.period.mixin", "image.mixin", "ni.identifier.mixin"]
    _inherits = {"ni.patient": "patient_id"}
    _check_company_auto = True
    _order = "period_start DESC, name DESC"

    company_id = fields.Many2one(
        related="patient_id.company_id",
        index=True,
        store=True,
    )
    name = fields.Char(
        "Encounter No.",
        copy=False,
        store=True,
        states=LOCK_STATE_DICT,
        index=True,
        compute="_compute_name",
    )
    identifier = fields.Char("Encounter No.")
    color = fields.Integer()
    class_id = fields.Many2one(
        "ni.encounter.class",
        "Classification",
        index=True,
        required=True,
        states=LOCK_STATE_DICT,
        help="Classification of patient encounter",
        ondelete="restrict",
        tracking=True,
    )
    period_start = fields.Datetime(
        readonly=True, states={"draft": [("readonly", False)]}
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
    patient_name = fields.Char(related="patient_id.name", readonly=False)

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
        [
            ("routing", "Routine"),
            ("urgent", "Urgent"),
            ("asap", "ASAP"),
            ("stat", "STAT"),
        ],
        default="routing",
        tracking=True,
        required=True,
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
        "ni.encounter.location",
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
    chief_complaint = fields.Text(
        "Chief Complaint", tracking=True, states=LOCK_STATE_DICT
    )
    chief_complaint_uid = fields.Many2one("res.users", readonly=True, copy=False)
    chief_complaint_date = fields.Datetime(readonly=True, copy=False)

    history_of_present_illness = fields.Html(
        "History of Present Illness", tracking=True, states=LOCK_STATE_DICT
    )
    history_of_present_illness_uid = fields.Many2one(
        "res.users", readonly=True, copy=False
    )
    history_of_present_illness_date = fields.Datetime(readonly=True, copy=False)

    review_of_systems = fields.Html(
        "Review of Systems", tracking=True, states=LOCK_STATE_DICT
    )
    review_of_systems_uid = fields.Many2one("res.users", readonly=True, copy=False)
    review_of_systems_date = fields.Datetime(readonly=True, copy=False)

    physical_exam = fields.Html(
        "Physical Examination", tracking=True, states=LOCK_STATE_DICT
    )
    physical_exam_uid = fields.Many2one("res.users", readonly=True, copy=False)
    physical_exam_date = fields.Datetime(readonly=True, copy=False)

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
    origin_date = fields.Date(
        string="Transfer At",
        states=LOCK_STATE_DICT,
        tracking=True,
        help="When origin organization request to transfer",
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
    re_admit_encounter_id = fields.Many2one(
        "ni.encounter",
        "Re-Admission Of",
        states=LOCK_STATE_DICT,
        tracking=True,
        domain="[('patient_id', '=', patient_id),"
        " ('id', '!=', id),"
        " ('state', '=', 'finished')]",
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
        "encounter_id",
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
    participant_ids = fields.One2many(
        "ni.encounter.participant", "encounter_id", states=LOCK_STATE_DICT
    )
    participant_count = fields.Integer(compute="_compute_participant")

    workflow_event_ids = fields.One2many("ni.workflow.event", "encounter_id")
    workflow_request_ids = fields.One2many("ni.workflow.request", "encounter_id")

    _sql_constraints = [
        (
            "company_id__name__uniq",
            "unique (company_id, name)",
            "This Encounter No. already exists!",
        ),
    ]

    @api.depends("identifier")
    def _compute_name(self):
        for rec in self:
            rec.name = rec.identifier

    @api.depends("location_history_ids")
    def _compute_location_history_count(self):
        for rec in self:
            rec.location_history_count = len(rec.location_history_ids)

    @api.depends("participant_ids")
    def _compute_participant(self):
        for rec in self:
            rec.participant_count = len(rec.participant_ids)

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

    @api.onchange("re_admit")
    def onchange_re_admit(self):
        for rec in self:
            if rec.re_admit:
                last_enc = self.search(
                    [
                        ("patient_id", "=", rec.patient_id.id),
                        ("state", "=", "finished"),
                    ],
                    order="period_end desc, period_start desc",
                    limit=1,
                )
                if last_enc:
                    rec.re_admit_encounter_id = last_enc[0]

    @api.onchange("country_id")
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange("state_id")
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

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

    @api.constrains("origin_partner_id", "origin_date", "period_start")
    def check_origin_date(self):
        for rec in self:
            if rec.origin_date and not rec.origin_partner_id:
                raise _("Transfer from must not be null when transfer at is present")
            if rec.origin_date and rec.origin_date > rec.period_start:
                raise _("Transfer date must not be after encounter start date")

    def name_get(self):
        return [(enc.id, enc._get_name()) for enc in self]

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
        if self._context.get("show_period"):
            name = "{}\n{} → {}".format(
                name, rec.period_start, rec.period_end or _("Now")
            )
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
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._update_sign_fields(vals)

        result = super().create(vals_list)
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
        self._update_sign_fields(vals)

        res = super().write(vals)
        if "state" in vals:
            for enc in self:
                enc.patient_id._compute_encounter()
        return res

    def _update_sign_fields(self, vals):
        ts = fields.Datetime.now()
        for f in SIGN_FILEDS:
            if f in vals and vals[f]:
                f_uid = "{}_uid".format(f)
                f_date = "{}_date".format(f)
                if f_uid not in vals:
                    vals[f_uid] = self.env.uid
                if f_date not in vals:
                    vals[f_date] = ts
        return vals

    def get_last_location(self):
        enc_location = self.env["ni.encounter.location"].sudo()
        return enc_location.search(
            args=[("encounter_id", "=", self.id)], order="period_start DESC", limit=1
        )

    def _create_location_hist(self, location, start=None):
        self.ensure_one()
        encounter_location = self.env["ni.encounter.location"].sudo()
        encounter_location.create(
            {
                "company_id": self.company_id.id,
                "encounter_id": self.id,
                "location_id": location,
                "period_start": start or fields.Datetime.now(),
            }
        )

    def action_confirm(self):
        today = fields.datetime.now()
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
                enc.participant_ids.action_stop()

    def action_entered_in_error(self):
        self.write({"state": "entered-in-error"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancelled"})
