#  Copyright (c) 2021 Piruin P.

import base64

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


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
    name = fields.Char("Name", require=True, compute="_compute_name", store=False)
    title = fields.Many2one("res.partner.title", "Title", tracking=True)
    firstname = fields.Char("Firstname", copy=False, require=True, tracking=True)
    lastname = fields.Char("Lastname", copy=False, tracking=True)
    country_id = fields.Many2one("res.country", "Nationality (Country)", tracking=True)
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

    private_mobile = fields.Char(
        related="home_address_id.mobile",
        related_sudo=False,
        readonly=False,
        tracking=True,
        string="Private Phone",
        groups="hr.group_hr_user",
    )
    home_address_id = fields.Many2one(
        "res.partner",
        "Home Address",
        help="the private address of the Patient",
        tracking=True,
        check_company=True,
        copy=False,
    )
    home_phone = fields.Char(
        related="home_address_id.phone",
        related_sudo=False,
        readonly=False,
        tracking=True,
        string="Home Phone",
        groups="hr.group_hr_user",
    )
    work_address_id = fields.Many2one(
        "res.partner",
        "Work Address",
        help="Work contract of Patient",
        tracking=True,
        check_company=True,
        copy=False,
        domain=[("is_company", "=", True)],
    )
    work_phone = fields.Char(
        related="work_address_id.phone",
        related_sudo=False,
        readonly=False,
        tracking=True,
        string="Work Phone",
        groups="hr.group_hr_user",
    )
    job_title = fields.Char(tracking=True)

    hometown_address_id = fields.Many2one(
        "res.partner",
        "Hometown Address",
        domain=[("type", "=", "private")],
        help="hometown address of the Patient",
        tracking=True,
        check_company=True,
        copy=False,
    )
    category_ids = fields.Many2many(
        "ni.patient.category",
        "ni_patient_category_rel",
        "patient_id",
        "category_id",
        string="Category",
    )
    encounter_ids = fields.One2many("ni.encounter", "patient_id", string="Encounter")
    current_encounter_id = fields.Many2one(
        "ni.encounter", compute="_compute_current_encounter_id", require=False
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

    @api.depends("encounter_ids")
    def _compute_current_encounter_id(self):
        enc = (
            self.env["ni.encounter"]
            .search([("patient_id", "in", self.ids)], order="patient_id, id DESC")
            .filtered(lambda en: en.is_present)
        )
        for rec in self:
            enc_ids = enc.filtered(lambda en: en.patient_id.id == rec.id)
            rec.current_encounter_id = enc_ids[0] if enc_ids else None

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            "nirun_patient", "static/src/img", "default_patient.png"
        )
        return base64.b64encode(open(image_path, "rb").read())

    image_1920 = fields.Image(default=_default_image, copy=False)

    @api.constrains("firstname", "lastname")
    def _check_name(self):
        for record in self:
            if not (record.firstname or record.lastname):
                raise ValidationError(_("No name set."))

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

    @api.depends("title", "firstname", "lastname")
    def _compute_name(self):
        for record in self:
            names = [
                name.strip() if name else None
                for name in [record.title.shortcut, record.firstname, record.lastname]
            ]
            computed_name = " ".join(filter(None, names))
            record.name = computed_name if computed_name else _("New Patient")

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
