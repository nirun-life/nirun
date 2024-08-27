#  Copyright (c) 2021-2023 NSTDA

import base64

from odoo import _, api, fields, models
from odoo.modules.module import get_module_resource

ENCOUNTER_INACTIVE_STATE = ["entered-in-error", "cancelled"]

SIGN_FILEDS = [
    "past_medical_history",
]


class Patient(models.Model):
    _name = "ni.patient"
    _description = "Patient"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "image.mixin",
        "ni.identifier.mixin",
        "ni.export.data.logger",
    ]
    _inherits = {"res.partner": "partner_id"}
    _check_company_auto = True
    _order = "name"
    _sign_fields = [
        "past_medical_history",
    ]

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            "ni_patient", "static/src/img", "default_image.png"
        )
        return base64.b64encode(open(image_path, "rb").read())

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
        "Related Partner",
        check_company=True,
        required=True,
        ondelete="restrict",
        domain="[('type', '=', 'contact'), ('is_company', '=', False)]",
        auto_join=True,
        help="Partner-related data of patient",
    )
    image_1920 = fields.Image(
        related="partner_id.image_1920", readonly=False, default=_default_image
    )
    image_1024 = fields.Image(related="partner_id.image_1024", readonly=False)
    image_512 = fields.Image(related="partner_id.image_512", readonly=False)
    image_256 = fields.Image(related="partner_id.image_256", readonly=False)
    image_128 = fields.Image(related="partner_id.image_128", readonly=False)

    name = fields.Char(
        related="partner_id.name", inherited=True, readonly=False, tracking=True
    )
    phone = fields.Char(
        related="partner_id.phone", inherited=True, readonly=False, tracking=True
    )
    mobile = fields.Char(
        related="partner_id.mobile", inherited=True, readonly=False, tracking=True
    )
    email = fields.Char(
        related="partner_id.email", inherited=True, readonly=False, tracking=True
    )
    other_address_id = fields.Many2one(
        "res.partner",
        "Other Address",
        domain="[('ref', '=', identifier), ('type', '=', 'private')]",
    )

    nationality_id = fields.Many2one(
        "res.country",
        "Nationality (Country)",
        tracking=True,
        default=lambda self: self.env.company.country_id,
    )
    identification_id = fields.Char(
        string="Identification No",
        related="partner_id.identification_id",
        copy=False,
        tracking=True,
        readonly=False,
        help="ID related to patient's nationality",
    )
    gender = fields.Selection(
        tracking=True,
        related="partner_id.gender",
        readonly=False,
        store=True,
    )
    birthdate = fields.Date(
        "Date of Birth", related="partner_id.birthdate", readonly=False, tracking=True
    )
    deceased_date = fields.Date(
        "Deceased Date",
        related="partner_id.deceased_date",
        readonly=False,
        tracking=True,
    )

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
            ("-", "Uneducated"),
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
        required=False,
        tracking=True,
        help="Education level according to ISCED",
    )
    study_field = fields.Char()
    study_school = fields.Char()

    encounter_ids = fields.One2many(
        "ni.encounter", "patient_id", "Encounter(s)", readonly=True
    )
    encounter_count = fields.Integer(compute="_compute_encounter", compute_sudo=True)
    encounter_id = fields.Many2one(
        "ni.encounter",
        "Encounter No.",
        compute="_compute_encounter",
        required=False,
        compute_sudo=True,
        store=True,
    )
    encounter_start = fields.Date(
        "Encounter Start",
        compute="_compute_encounter",
        required=False,
        compute_sudo=True,
    )
    is_encountering = fields.Boolean(
        compute="_compute_encounter", default=False, store=True, compute_sudo=True
    )
    presence_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("planned", "Planned"),
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
    location_id = fields.Many2one(related="encounter_id.location_id")
    active = fields.Boolean(default=True)

    past_medical_history = fields.Html("Past Medical History", tracking=True)
    past_medical_history_uid = fields.Many2one("res.users", readonly=True, copy=False)
    past_medical_history_date = fields.Datetime(readonly=True, copy=False)

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update(self._prepare_sign_field_vals(vals))
        return super().create(vals_list)

    def write(self, vals):
        vals.update(self._prepare_sign_field_vals(vals))
        return super().write(vals)

    _sql_constraints = [
        (
            "identifier_uniq",
            "unique (company_id, identifier)",
            _("Identifier must be unique !"),
        ),
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
        if self._context.get("show_identifier") and patient.identifier:
            name = "{}  {}".format(patient.identifier, name)
        if self._context.get("show_identification_id") and patient.identification_id:
            name = "{} ({})".format(name, patient.identification_id)
        if self._context.get("show_gender_age"):
            gender_age = []
            if patient.gender in ["male", "female"]:
                gender_age.append(
                    dict(self._fields["gender"].selection(self))[self.gender]
                )
            if patient.age:
                gender_age.append(_("{} years old").format(patient.age))
            if gender_age:
                name = "{}\n{}".format(name, ", ".join(gender_age))
        elif self._context.get("show_age") and patient.age:
            name = _("{} ({}Y)").format(name, patient.age)
        return name

    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += [
                "|",
                "|",
                ("name", operator, name),
                ("identifier", operator, name),
                ("identification_id", operator, name),
            ]

        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.name = rec.partner_id.name
                rec.nationality_id = rec.partner_id.country_id
                if not rec._origin.identification_id:
                    rec.identification_id = rec.partner_id.vat

    @api.depends("encounter_ids")
    def _compute_encounter(self):
        enc = self.env["ni.encounter"].search(
            [
                ("patient_id", "in", self.ids),
                ("state", "not in", ENCOUNTER_INACTIVE_STATE),
            ],
            order="id DESC",
        )
        for rec in self:
            enc_ids = enc.filtered(lambda en: en.patient_id.id == rec.id)
            rec.encounter_count = len(enc_ids)
            latest_enc = enc_ids[0] if enc_ids else None
            if latest_enc and latest_enc.state in ["draft", "planned", "in-progress"]:
                rec.update(
                    {
                        "encounter_id": latest_enc.id,
                        "encounter_start": latest_enc.period_start,
                        "is_encountering": True,
                        "presence_state": latest_enc.state,
                    }
                )
            elif latest_enc and latest_enc.state in ["finished"]:
                rec.update(
                    {
                        "encounter_id": None,
                        "encounter_start": None,
                        "is_encountering": False,
                        "presence_state": latest_enc.state,
                    }
                )
            else:
                rec.update(
                    {
                        "encounter_id": None,
                        "encounter_start": None,
                        "is_encountering": False,
                        "presence_state": "unknown",
                    }
                )
            if rec.deceased:
                rec.presence_state = "deceased"

    @api.onchange("country_id")
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange("state_id")
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    def action_encounter(self):
        action_rec = self.env.ref("ni_patient.ni_encounter_action").sudo()
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
            "res_id": self.encounter_id.id,
        }
