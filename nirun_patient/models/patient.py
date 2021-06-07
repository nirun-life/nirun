#  Copyright (c) 2021 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

ENCOUNTER_INACTIVE_STATE = ["entered-in-error", "draft", "cancelled"]


class Partner(models.Model):
    _inherit = "res.partner"

    patient = fields.Boolean(
        compute="_compute_patient",
        store=True,
        help="Check this box if this contact is an Patient.",
        compute_sudo=True,
    )
    patient_ids = fields.One2many("ni.patient", "partner_id", "Patient Records")
    patient_id = fields.Many2one(
        "ni.patient", "Patient Record", compute="_compute_patient", compute_sudo=True
    )

    @api.depends("patient_ids")
    def _compute_patient(self):
        for rec in self:
            rec.patient = bool(rec.patient_ids)
            rec.patient_id = rec.patient_ids.filtered(
                lambda p: p.company_id == self.env.company
            )


class Patient(models.Model):
    _name = "ni.patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]
    _check_company_auto = True
    _order = "name"

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    partner_id = fields.Many2one(
        "res.partner",
        "Patient",
        copy=False,
        check_company=True,
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
        domain="[('type', '=', 'contact'), ('is_company', '=', False)]",
        help="Contact information of patient",
    )
    image_1920 = fields.Image(related="partner_id.image_1920", readonly=False)
    image_1024 = fields.Image(related="partner_id.image_1024", readonly=False)
    image_512 = fields.Image(related="partner_id.image_512", readonly=False)
    image_256 = fields.Image(related="partner_id.image_256", readonly=False)
    image_128 = fields.Image(related="partner_id.image_128", readonly=False)
    name = fields.Char(
        related="partner_id.name", readonly=False, store=True, index=True
    )
    phone = fields.Char(related="partner_id.phone", readonly=False)
    mobile = fields.Char(related="partner_id.mobile", readonly=False)
    email = fields.Char(related="partner_id.email", readonly=False)

    code = fields.Char("Patient No.", copy=False, tracking=True)

    country_id = fields.Many2one(
        "res.country",
        "Nationality (Country)",
        tracking=True,
        default=lambda self: self.env.company.country_id,
    )
    identification_id = fields.Char(
        string="Identification No",
        copy=False,
        tracking=True,
        help="ID related to patient's nationality",
    )
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")], tracking=True,
    )
    birthdate = fields.Date("Date of Birth", tracking=True)
    age = fields.Char("Age", compute="_compute_age", compute_sudo=True)
    age_years = fields.Integer(
        "Age (years)",
        compute="_compute_age",
        compute_sudo=True,
        inverse="_inverse_age",
        store=True,
    )
    deceased_date = fields.Date("Deceased Date", tracking=True, copy=False)
    deceased = fields.Boolean("Deceased", compute="_compute_is_deceased", store=True)

    marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("married", "Married"),
            ("cohabitant", "Legal Cohabitant"),
            ("separated", "Separated"),
            ("widower", "Widower"),
            ("divorced", "Divorced"),
            ("polygamous", "Polygamous"),
            ("unknown", "Unknown"),
        ],
        string="Marital Status",
        default="unknown",
        tracking=True,
    )
    father_name = fields.Char("Father Complete Name")
    mother_name = fields.Char("Mother Complete Name")
    spouse_name = fields.Char("Spouse Complete Name")
    sibling_count = fields.Integer("Number of Sibling")
    birth_order = fields.Integer("Birth Order")
    children_count = fields.Integer("Number of Children")

    education_level = fields.Selection(
        [
            ("0", "Early Childhood"),
            ("1", "Primary"),
            ("2", "Lower Secondary"),
            ("3", "Upper Secondary"),
            ("4", "Post-Secondary"),
            ("5", "Short-cycle Tertiary"),
            ("6", "Bachelor"),
            ("7", "Master"),
            ("8", "Doctor"),
        ],
        require=False,
        tracking=True,
        help="Education level according to ISCED",
    )
    study_field = fields.Char()
    study_school = fields.Char()

    encounter_ids = fields.One2many(
        "ni.encounter", "patient_id", "Encounter(s)", readonly=True
    )
    encounter_count = fields.Integer(compute="_compute_encounter", compute_sudo=True)
    last_encounter_id = fields.Many2one(
        "ni.encounter",
        "Last Encounter ",
        compute="_compute_encounter",
        require=False,
        compute_sudo=True,
        store=True,
    )
    encountering_id = fields.Many2one(
        "ni.encounter",
        "Encounter No.",
        compute="_compute_encounter",
        require=False,
        compute_sudo=True,
        store=True,
    )
    performer_id = fields.Many2one(related="encountering_id.performer_id")

    encountering_start = fields.Date(
        "Encounter Start",
        compute="_compute_encounter",
        require=False,
        compute_sudo=True,
    )
    is_encountering = fields.Boolean(
        compute="_compute_encounter", default=False, store=True, compute_sudo=True
    )
    presence_state = fields.Selection(
        [
            ("planned", "Waiting"),
            ("in-progress", "In-Progress"),
            ("finished", "Discharged"),
            ("deceased", "Deceased"),
            ("unknown", "Unknown"),
        ],
        compute="_compute_encounter",
        default="unknown",
        store=True,
        compute_sudo=True,
    )
    location_id = fields.Many2one(related="encountering_id.location_id")

    gp_hospital_id = fields.Many2one(
        "res.partner", "Hospital", domain=[("is_company", "=", True)]
    )
    gp_id = fields.Many2one(
        "res.partner", "General Practitioner", domain=[("is_company", "=", False)]
    )

    _sql_constraints = [
        ("code_uniq", "unique (company_id, code)", _("Code must be unique !"),),
        (
            "partner_uniq",
            "unique (company_id, partner_id)",
            _("This contact have already registered as patient!"),
        ),
    ]

    def name_get(self):
        return [(patient.id, patient._name_get()) for patient in self]

    def _name_get(self):
        patient = self
        name = patient.name or ""
        if self._context.get("show_address"):
            name = patient.partner_id.with_context(show_address=True).name_get()
        if self._context.get("show_code") and patient.code:
            name = "[{}] {}".format(patient.code, name)

        return name

    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += ["|", ("name", operator, name), ("code", operator, name)]
        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(ids).with_user(name_get_uid))

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.country_id = rec.partner_id.country_id
                if not rec._origin.identification_id:
                    rec.identification_id = rec.partner_id.vat

    @api.onchange("gp_id")
    def onchange_gp_id(self):
        for rec in self:
            if rec.gp_id and rec.gp_id.parent_id:
                rec.gp_hospital_id = rec.gp_id.parent_id

    @api.depends("encounter_ids")
    def _compute_encounter(self):
        enc = self.env["ni.encounter"].search(
            [
                ("patient_id", "in", self.ids),
                ("state", "not in", ENCOUNTER_INACTIVE_STATE),
            ],
            order="patient_id, id DESC",
        )
        for rec in self:
            enc_ids = enc.filtered(lambda en: en.patient_id.id == rec.id)
            rec.encounter_count = len(enc_ids)
            last_enc = enc_ids[0] if enc_ids else None
            if last_enc and last_enc.state == "in-progress":
                rec.update(
                    {
                        "last_encounter_id": last_enc.id,
                        "encountering_id": last_enc.id,
                        "encountering_start": last_enc.period_start,
                        "is_encountering": True,
                        "presence_state": last_enc.state,
                    }
                )
            elif last_enc and last_enc.state in ["finished", "planned"]:
                rec.update(
                    {
                        "last_encounter_id": last_enc.id,
                        "encountering_id": None,
                        "encountering_start": None,
                        "is_encountering": False,
                        "presence_state": last_enc.state,
                    }
                )
            else:
                rec.update(
                    {
                        "last_encounter_id": None,
                        "encountering_id": None,
                        "encountering_start": None,
                        "is_encountering": False,
                        "presence_state": "unknown",
                    }
                )
            if rec.deceased:
                rec.presence_state = "deceased"

    @api.constrains("birthdate")
    def _check_birthdate(self):
        """ Not allow birthdates in the future. """
        for record in self:
            if not record.birthdate:
                continue
            if record.birthdate > fields.date.today():
                raise ValidationError(_("Patient cannot be born in the future.",))

    @api.constrains("deceased_date")
    def _check_deceased_date(self):
        for record in self:
            if not record.deceased_date:
                continue
            if record.deceased_date > fields.date.today():
                raise ValidationError(
                    _("You should not forecast that Patient will die!",)
                )
            if record.birthdate and record.deceased_date < record.birthdate:
                raise ValidationError(_("Patient cannot die before they was born!",))

    @api.constrains("gp_id", "gp_hospital_id")
    def _check_general_practitioner(self):
        for rec in self:
            if (
                rec.gp_id
                and rec.gp_id.parent_id
                and rec.gp_hospital_id
                and rec.gp_id.parent_id != rec.gp_hospital_id
            ):
                raise ValidationError(
                    _("General Practitioner's Company and Hospital must be the same!")
                )

    @api.model
    def _compute_is_deceased(self):
        for record in self:
            record.deceased = bool(record.deceased_date)

    @api.depends("birthdate", "deceased_date")
    def _compute_age(self):
        for rec in self:
            rec.age = None
            rec.age_years = 0
            if rec.birthdate:
                dt = (
                    rec.deceased_date
                    if rec.deceased_date
                    else fields.Date.context_today(self)
                )
                rd = relativedelta(dt, rec.birthdate)
                rec.age = self._format_age(rd)
                rec.age_years = rd.years

    @api.model
    def _format_age(self, delta):
        result = []
        if delta.years > 0:
            result.append(_("%s Years") % delta.years)
        if delta.months > 0:
            result.append(_("%s Months") % delta.months)
        if delta.days > 0:
            result.append(_("%s Days") % delta.days)
        return " ".join(result) or None

    def _inverse_age(self):
        today = fields.date.today()
        for record in self.filtered(lambda r: not (r.deceased_date and r.birthdate)):
            record.birthdate = today - relativedelta(years=record.age_years)

    def action_encounter(self):
        action_rec = self.env.ref("nirun_patient.encounter_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.ids[0],
                "default_patient_id": self.ids[0],
            }
        )
        action["context"] = ctx
        return action

    def action_current_encounter(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "ni.encounter",
            "views": [[False, "form"]],
            "res_id": self.encountering_id.id,
        }
