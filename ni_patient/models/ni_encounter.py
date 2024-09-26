#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.models import Command

LOCK_STATE_DICT = {
    "cancelled": [("readonly", True)],
    "entered-in-error": [("readonly", True)],
    "finished": [("readonly", True)],
}


class Encounter(models.Model):
    _name = "ni.encounter"
    _description = "Encounter"
    _inherit = [
        "mail.thread",
        "ni.period.mixin",
        "image.mixin",
        "ni.identifier.mixin",
        "ni.export.data.logger",
        "age.mixin",
    ]
    _inherits = {"ni.patient": "patient_id"}
    _check_company_auto = True
    _order = "period_start DESC, name DESC"
    _sign_fields = [
        "chief_complaint",
        "history_of_present_illness",
        "past_medical_history",
        "review_of_systems",
        "physical_exam",
    ]

    @api.model
    def default_get(self, fields):
        comp = self.env.company
        if self.env.context.get("default_company_id"):
            comp_id = self.env.context["default_company_id"]
            comp = self.env["res.company"].browse(comp_id)[0]
        if self.env.context.get("default_patient_id"):
            pat_id = self.env.context["default_patient_id"]
            comp = self.env["ni.patient"].browse(pat_id)[0].company_id

        if "default_class_id" not in self.env.context and comp.encounter_class_id:
            self = self.with_context(
                default_class_id=comp.encounter_class_id.id,
            )
        return super(Encounter, self).default_get(fields)

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
    identifier = fields.Char(
        "Encounter No.",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="ใส่เลขรับบริการที่ทางหน่วยงานต้องการ หากไม่ระบุระบบจะสร้างให้อัตโนมัติ",
    )
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
    class_decoration = fields.Selection(related="class_id.decoration")
    auto_close = fields.Boolean(related="class_id.auto_close")
    period_start = fields.Datetime(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    period_end = fields.Datetime(readonly=True)
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        readonly=True,
        required=True,
        ondelete="cascade",
        states={"draft": [("readonly", False)]},
        auto_join=True,
        index=True,
    )
    patient_name = fields.Char(related="patient_id.name", readonly=False)
    birthdate = fields.Date(related="patient_id.birthdate")
    age_init = fields.Integer(related="patient_id.age_init")
    age_init_date = fields.Date(related="patient_id.age_init_date")
    display_age = fields.Char(string="At Age")

    patient_identifier = fields.Char(related="patient_id.identifier")

    @api.depends("birthdate", "deceased_date", "age_init", "period_start")
    def _compute_age(self):
        for rec in self:
            if rec.birthdate:
                rec._compute_age_from_birthdate(rec.period_start)
            elif rec.age_init:
                rec._compute_age_from_init(rec.period_start)
            else:
                rec.update({"age": 0, "display_age": None})

    other_address_id = fields.Many2one(
        "res.partner",
        "Other Address",
        domain="[('ref', '=', patient_identifier), ('type', '=', 'private')]",
    )

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
            ("routine", "Routine"),
            ("urgent", "Urgent"),
            ("asap", "ASAP"),
            ("stat", "STAT"),
        ],
        "Triage",
        default="routine",
        tracking=True,
        required=True,
        states=LOCK_STATE_DICT,
    )
    priority_decoration = fields.Selection(
        [
            ("routine", "muted"),
            ("urgent", "info"),
            ("asap", "warning"),
            ("stat", "danger"),
        ],
        compute="_compute_priority_decoration",
    )

    @api.depends("priority")
    def _compute_priority_decoration(self):
        for rec in self:
            rec.priority_decoration = rec.priority

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

    past_medical_history = fields.Html(
        "Past Medical History", tracking=True, states=LOCK_STATE_DICT
    )
    past_medical_history_uid = fields.Many2one("res.users", readonly=True, copy=False)
    past_medical_history_date = fields.Datetime(readonly=True, copy=False)

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

    show_special = fields.Boolean(related="class_id.special")
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

    # Admission
    is_admission = fields.Boolean(related="class_id.admission", store=True)
    pre_admission_identifier = fields.Char(
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
    re_admission = fields.Boolean(
        "Re-Admission",
        states=LOCK_STATE_DICT,
        tracking=True,
        help="The type of hospital re-admission that has occurred (if any). "
        "If the value is absent, then this is not identified as a readmission",
    )
    re_admission_reason = fields.Text(
        "Re-Admission Reason",
        states=LOCK_STATE_DICT,
        tracking=True,
    )
    re_admission_encounter_id = fields.Many2one(
        "ni.encounter",
        "Re-Admission Of",
        states=LOCK_STATE_DICT,
        tracking=True,
        domain="[('patient_id', '=', patient_id),"
        " ('id', '!=', id),"
        " ('state', '=', 'finished')]",
    )
    discharge_status_id = fields.Many2one(
        "ni.encounter.discharge.status",
        "Discharge Status",
        help="Patient's status on discharge",
        tracking=True,
        states=LOCK_STATE_DICT,
    )
    discharge_disposition_id = fields.Many2one(
        "ni.encounter.discharge.disposition",
        "Discharge Disposition",
        help="Category or kind of location after discharge",
        tracking=True,
        states=LOCK_STATE_DICT,
    )
    discharge_partner_id = fields.Many2one(
        "res.partner",
        "Destination",
        domain="[('is_company', '=', True)]",
        help="Location/organization to which the patient is discharged",
        tracking=True,
        states=LOCK_STATE_DICT,
    )
    discharge_note = fields.Text("Note", tracking=True)

    # Encounter Class configuration
    show_history = fields.Boolean(related="class_id.history")
    show_chief_complaint = fields.Boolean(related="class_id.chief_complaint")
    show_history_of_present_illness = fields.Boolean(
        related="class_id.history_of_present_illness"
    )
    show_review_of_systems = fields.Boolean(related="class_id.review_of_systems")
    show_physical_exam = fields.Boolean(related="class_id.physical_exam")
    show_vital_signs = fields.Boolean(related="class_id.vital_signs")
    show_laboratory = fields.Boolean(related="class_id.laboratory")
    show_problem_list = fields.Boolean(related="class_id.problem_list")
    show_medication = fields.Boolean(related="class_id.medication")
    show_procedure = fields.Boolean(related="class_id.procedure")
    show_questionnaire = fields.Boolean(related="class_id.questionnaire")
    show_document_ref = fields.Boolean(related="class_id.document_ref")
    show_service = fields.Boolean(related="class_id.service")
    show_participant = fields.Boolean(related="class_id.participant")
    show_careplan = fields.Boolean(related="class_id.careplan")
    show_order = fields.Boolean(related="class_id.order")

    # Participant
    participant_ids = fields.One2many(
        "ni.encounter.participant", "encounter_id", states=LOCK_STATE_DICT
    )
    participant_id = fields.Many2one(
        "ni.encounter.participant", compute="_compute_participant_id"
    )
    participant_title = fields.Many2one(
        "hr.job", related="participant_id.employee_id.job_id"
    )
    participant_count = fields.Integer(compute="_compute_participant")
    participate = fields.Boolean(
        compute="_compute_participant",
        help="Indicate whether current user is already participated",
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

    @api.depends("participant_ids")
    def _compute_participant_id(self):
        for rec in self:
            if not rec.participant_ids:
                rec.participant_id = None
                continue
            active_participant = rec.participant_ids.filtered_domain(
                [("period_end", "=", False)]
            )
            if active_participant:
                rec.participant_id = active_participant[0].id
            else:
                rec.participant_id = rec.participant_ids[0].id

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
        uid = self.env.uid
        for rec in self:
            if rec.state in ["finished"]:
                user_ids = rec.participant_ids.mapped("user_id")
            else:
                user_ids = rec.participant_ids.filtered(
                    lambda p: not p.period_end
                ).mapped("user_id")
            rec.update(
                {"participant_count": len(user_ids), "participate": uid in user_ids.ids}
            )

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
            self.pre_admission_identifier = self.patient_id.identifier
            self.past_medical_history = self.patient_id.past_medical_history
            self.past_medical_history_uid = self.patient_id.past_medical_history_uid
            self.past_medical_history_date = self.patient_id.past_medical_history_date

    @api.onchange("re_admission")
    def onchange_re_admit(self):
        for rec in self:
            if rec.re_admission:
                last_enc = self.search(
                    [
                        ("patient_id", "=", rec.patient_id.id),
                        ("state", "=", "finished"),
                    ],
                    order="period_end desc, period_start desc",
                    limit=1,
                )
                if last_enc:
                    rec.re_admission_encounter_id = last_enc[0]

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

    @api.constrains(
        "discharge_status_id",
        "discharge_disposition_id",
    )
    def check_discharge_status_and_disposition(self):
        for rec in self:
            if (
                rec.discharge_status_id.disposition_ids
                and rec.discharge_disposition_id
                not in rec.discharge_status_id.disposition_ids
            ):
                raise ValidationError(
                    _("Inconsistency between discharge status and disposition")
                )

    def name_get(self):
        return [(enc.id, enc._get_name()) for enc in self]

    def _get_name(self):
        self.ensure_one()
        rec = self
        name = rec.name
        if self._context.get("show_class"):
            name = "{}/{}".format(name, rec.class_id.code or rec.class_id.name)
        if self._context.get("show_patient") or self._context.get("show_patient_name"):
            name = "{} {}".format(name, rec.patient_id.name)
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
            vals.update(self._prepare_sign_field_vals(vals))

            if "location_id" in vals and vals.get("location_id"):
                vals.update(
                    self._prepare_new_location_hist_vals(
                        vals["location_id"], vals.get("period_start")
                    )
                )
            if (
                self._identifier_field not in vals
                or (
                    vals.get(self._identifier_field, self._identifier_default)
                    or self._identifier_default
                )
                == self._identifier_default
            ):
                enc_class = self.env["ni.encounter.class"].browse(vals["class_id"])
                if not enc_class or not enc_class.sequence_id:
                    continue
                seq_date = fields.Date.today()
                if self._identifier_ts_field in vals:
                    seq_date = fields.Datetime.context_timestamp(
                        self,
                        fields.Datetime.to_datetime(vals[self._identifier_ts_field]),
                    )
                vals[self._identifier_field] = enc_class.sequence_id.next_by_id(
                    seq_date
                )

        result = super().create(vals_list)
        result.patient_id._compute_encounter()
        return result

    def write(self, vals):
        vals.update(self._prepare_sign_field_vals(vals))

        if "location_id" in vals and vals.get("location_id"):
            vals.update(self._prepare_new_location_hist_vals(vals["location_id"]))
            enc = self.filtered_domain([("location_id", "!=", vals["location_id"])])
            enc.location_history_ids.filtered_domain(
                [("period_end", "=", False)]
            ).action_stop()

        result = super().write(vals)

        if "state" in vals:
            for enc in self:
                enc.patient_id._compute_encounter()
        return result

    @api.model
    def _prepare_sign_field_vals(self, vals):
        value = {}
        ts = fields.Datetime.now()
        for f in self._sign_fields:
            if f in vals and vals[f]:
                f_uid = "{}_uid".format(f)
                f_date = "{}_date".format(f)
                if f_uid not in vals:
                    value[f_uid] = self.env.uid
                if f_date not in vals:
                    value[f_date] = ts
        return value

    @api.model
    def _prepare_new_location_hist_vals(self, location, start=None):
        return {
            "location_history_ids": [
                Command.create(
                    {
                        "company_id": self.company_id.id,
                        "encounter_id": self.id,
                        "location_id": location,
                        "period_start": start or fields.Datetime.now(),
                    }
                )
            ]
        }

    def action_confirm(self):
        now = fields.datetime.now()
        for enc in self:
            if not enc.period_start:
                raise ValidationError(
                    _("Verified encounter must defined start date (since)")
                )
            if enc.state == "draft":
                if now < enc.period_start:
                    enc.update({"state": "planned"})
                else:
                    enc.update({"state": "in-progress"})
                if not enc.participate and self.env.user.employee_id:
                    enc.action_participate()
            elif enc.state == "planned":
                enc.update(
                    {"state": "in-progress", "period_start": fields.Datetime.now()}
                )
                if not enc.participate and self.env.user.employee_id:
                    enc.action_participate()
            else:
                raise ValidationError(
                    _("Invalid State!, Please contact your system administrator")
                )

    def action_close(self, vals=None):
        for enc in self:
            if enc.state != "in-progress":
                raise ValidationError(_("Must be in-progress state"))

        vals = dict(vals or {"state": "finished", "period_end": fields.datetime.now()})
        self.participant_ids.action_stop()
        self.write(vals)
        for enc in self.filtered(
            lambda e: e.past_medical_history != e.patient_id.past_medical_history
        ):
            enc.patient_id.write(
                {
                    "past_medical_history": enc.past_medical_history,
                    "past_medical_history_uid": enc.past_medical_history_uid.id,
                    "past_medical_history_date": enc.past_medical_history_date,
                }
            )

    def action_entered_in_error(self):
        self.write({"state": "entered-in-error", "active": False})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_encounter_location(self):
        self.ensure_one()
        action_rec = self.env.ref("ni_patient.ni_encounter_location_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_encounter_id": self.ids[0],
                "default_encounter_id": self.ids[0],
            }
        )
        action["context"] = ctx
        return action

    def action_encounter_participant(self):
        self.ensure_one()
        action_rec = self.env.ref("ni_patient.ni_encounter_participant_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_encounter_id": self.ids[0],
                "default_encounter_id": self.ids[0],
            }
        )
        action["context"] = ctx
        return action

    def action_participate(self, type_id=None, start=None):
        period_start = start or fields.Datetime.now()
        user = self.env["res.users"].browse(self.env.uid)
        if not user.employee_id:
            raise ValidationError(
                _(
                    "กรุณาติดต่อผู้ดูแลระบบเพือเพิ่มทะเบียนผู้ปฎิบัติงานก่อนบันทึกเป็นผู้มีส่วนร่วมในงานให้บริการ"
                )
            )
        val = {
            "user_id": user.id,
            "employee_id": user.employee_id.id,
            "period_start": period_start,
        }
        if type_id:
            val.update({"type_id": type_id if isinstance(type_id, int) else type_id.id})

        self.write({"participant_ids": [models.Command.create(val)]})

    def action_quit(self):
        self.participant_ids.filtered(
            lambda p: p.user_id.id == self.env.uid
        ).action_stop()
