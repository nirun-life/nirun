#  Copyright (c) 2021 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    patient = fields.Boolean(compute="_compute_patient", store=True)
    patient_ids = fields.One2many("ni.patient", "partner_id")
    patient_related_person = fields.Boolean(
        compute="_compute_patient_related_person", store=True
    )

    @api.depends("patient_ids")
    def _compute_patient(self):
        for rec in self:
            rec.patient = bool(rec.patient_ids)

    @api.depends("parent_id")
    def _compute_patient_related_person(self):
        for rec in self:
            rec.patient_related_person = rec.parent_id and rec.parent_id.patient


class Patient(models.Model):
    _name = "ni.patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]
    _check_company_auto = True

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    identifier_number = fields.Char(
        "HN", copy=False, tracking=True, help="Hospital Identification Number"
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Contact Information",
        required=True,
        copy=False,
        ondelete="restrict",
        domain="[('type', '=', 'contact'), ('is_company', '=', False)]",
        help="Contact information of patient",
        check_company=True,
    )
    image_1920 = fields.Image(related="partner_id.image_1920")
    image_1024 = fields.Image(related="partner_id.image_1024")
    image_512 = fields.Image(related="partner_id.image_512")
    image_256 = fields.Image(related="partner_id.image_256")
    image_128 = fields.Image(related="partner_id.image_128")

    name = fields.Char(related="partner_id.name", store=True, index=True)
    display_name = fields.Char(
        related="partner_id.display_name", store=True, index=True
    )
    contact_address = fields.Char(
        related="partner_id.contact_address", string="Address"
    )

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
        groups="hr.group_hr_user",
        tracking=True,
        help="Education level according to ISCED",
    )
    study_field = fields.Char()
    study_school = fields.Char()

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        default="male",
        tracking=True,
    )
    marital_status = fields.Selection(
        [
            ("single", "Single"),
            ("married", "Married"),
            ("cohabitant", "Legal Cohabitant"),
            ("widower", "Widower"),
            ("divorced", "Divorced"),
        ],
        string="Marital Status",
        default="single",
        copy=False,
        tracking=True,
    )
    birthdate = fields.Date("Date of Birth", tracking=True, copy=False)
    age = fields.Char("Age", compute="_compute_age")
    age_years = fields.Integer("Age (years)", compute="_compute_age")
    deceased_date = fields.Date("Deceased Date", tracking=True, copy=False)
    deceased = fields.Boolean("Deceased", compute="_compute_is_deceased")

    category_ids = fields.Many2many(
        "ni.patient.category",
        "ni_patient_category_rel",
        "patient_id",
        "category_id",
        string="Category",
    )
    encounter_ids = fields.One2many(
        "ni.encounter", "patient_id", readonly=True, string="Encounter"
    )
    encounter_count = fields.Integer(compute="_compute_encounter_count")
    encountering_id = fields.Many2one(
        "ni.encounter",
        compute="_compute_encountering",
        require=False,
        compute_sudo=True,
        store=True,
    )
    encountering_start = fields.Date(
        compute="_compute_encountering", require=False, compute_sudo=True
    )
    is_encountering = fields.Boolean(
        compute="_compute_encountering", default=False, store=True, compute_sudo=True
    )

    diagnosis_ids = fields.One2many(
        "ni.patient.condition.latest", "patient_id", string="Diagnosis", readonly=True
    )

    _sql_constraints = [
        (
            "identifier_number_uniq",
            "unique (company_id, identifier_number)",
            _("Identifier must be unique !"),
        )
    ]

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.country_id = rec.partner_id.country_id
                if not rec._origin.identification_id:
                    rec.identification_id = rec.partner_id.vat

    def _compute_encounter_count(self):
        for rec in self:
            rec.encounter_count = len(rec.encounter_ids)

    @api.depends("encounter_ids")
    def _compute_encountering(self):
        enc = (
            self.env["ni.encounter"]
            .search([("patient_id", "in", self.ids)], order="patient_id, id DESC")
            .filtered(lambda en: en.is_present)
        )
        for rec in self:
            enc_ids = enc.filtered(lambda en: en.patient_id.id == rec.id)
            if enc_ids:
                rec.update(
                    {
                        "encountering_id": enc_ids[0].id,
                        "encountering_start": enc_ids[0].period_start,
                        "is_encountering": True,
                    }
                )
            else:
                # encountering_start must have value before it used to show at
                # 'statinfo' button and will be error if none. 'invisible' can't
                # help to prevent error
                rec.update(
                    {
                        "encountering_id": None,
                        "encountering_start": fields.Date.today(),
                        "is_encountering": False,
                    }
                )

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
            record.birthdate = today - relativedelta(years=record.age)

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
