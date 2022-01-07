#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models

ENCOUNTER_INACTIVE_STATE = ["entered-in-error", "cancelled"]


class Patient(models.Model):
    _name = "ni.patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]
    _inherits = {"res.partner": "partner_id"}
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
        "Related Partner",
        check_company=True,
        required=True,
        ondelete="restrict",
        domain="[('type', '=', 'contact'), ('is_company', '=', False)]",
        auto_join=True,
        help="Partner-related data of patient",
    )
    image_1920 = fields.Image(related="partner_id.image_1920", readonly=False)
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

    code = fields.Char("Patient No.", copy=False, tracking=True)

    nationality_id = fields.Many2one(
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
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
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
    encounter_id = fields.Many2one(
        "ni.encounter",
        "Encounter No.",
        compute="_compute_encounter",
        require=False,
        compute_sudo=True,
        store=True,
    )
    performer_id = fields.Many2one(related="encounter_id.performer_id")

    encounter_start = fields.Date(
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
            ("draft", "Draft"),
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
    location_id = fields.Many2one(related="encounter_id.location_id")
    active = fields.Boolean(default=True)

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
            "res_id": self.encounter_id.id,
        }
