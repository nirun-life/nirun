#  Copyright (c) 2023 NSTDA
import base64
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from odoo.addons.ni_observation.models import ni_observation_vitalsign_mixin as vs

_logger = logging.getLogger(__name__)

PATIENT_FIELD = [
    "company_id",
    "partner_id",
    "title",
    "name",
    "image_1920",
    "gender",
    "street",
    "street2",
    "city",
    "state_id",
    "zip",
    "country_id",
    "nationality_id",
    "birthdate",
    "blood_abo",
    "blood_rh",
    "condition_ids",
    "coverage_type_ids",
]

ENCOUNTER_FIELD = [
    "company_id",
    "patient_id",
    "chief_complaint",
    "reason_ids",
    "priority",
    "class_id",
    "identifier",
    "department_id",
    "performer_id",
    "allergy_code_ids",
] + vs.VITALSIGN_FIELDS


class Reception(models.Model):
    _name = "ni.reception"
    _description = "Reception"
    _inherit = [
        "ni.identifier.mixin",
        "ni.observation.vitalsign.mixin",
        "ni.observation.bloodgroup.mixin",
        "image.mixin",
    ]
    _rec_name = "identifier"
    _order = "create_date desc"

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            "ni_patient", "static/src/img", "default_image.png"
        )
        return base64.b64encode(open(image_path, "rb").read())

    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, required=True
    )
    partner_id = fields.Many2one("res.partner")
    patient_id = fields.Many2one("ni.patient", check_company=True)
    patient_age = fields.Integer(related="patient_id.age")
    title = fields.Many2one("res.partner.title")
    name = fields.Char(copy=False, required=True)
    image_1920 = fields.Image(default=_default_image)
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female")], required=True, default="male"
    )
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state")
    zip = fields.Char()
    country_id = fields.Many2one(
        "res.country", default=lambda self: self.env.company.country_id
    )
    email = fields.Char()
    mobile = fields.Char()
    phone = fields.Char()
    identification_id = fields.Char()
    nationality_id = fields.Many2one(
        "res.country", default=lambda self: self.env.company.country_id
    )
    birthdate = fields.Date()
    coverage_type_ids = fields.Many2many(
        "ni.coverage.type", "ni_reception_coverage_type", string="Coverage"
    )

    period_start = fields.Datetime(
        "Encounter Start", default=fields.datetime.now(), required=True
    )
    class_id = fields.Many2one("ni.encounter.class", required=True)
    chief_complaint = fields.Text()
    reason_ids = fields.Many2many(
        "ni.encounter.reason", "ni_reception_reason", "reception_id", "reason_id"
    )
    condition_problem_ids = fields.Many2many(
        "ni.condition.code",
        "ni_reception_condition",
        "reception_id",
        "code_id",
        "Chronic Condition",
    )
    allergy_code_ids = fields.Many2many(
        "ni.allergy.code",
        "ni_reception_allergy",
        "reception_id",
        "code_id",
        "Allergy",
    )
    priority = fields.Selection(
        [
            ("routine", "Routine"),
            ("asap", "ASAP"),
            ("urgent", "Urgent"),
            ("stat", "STAT"),
        ],
        "Triage",
        default="routine",
        required=True,
    )

    encounter_identifier_type = fields.Selection(
        [("auto", "Auto Generate"), ("manual", "Manual")],
        default="auto",
        required=True,
        copy=False,
    )
    encounter_identifier = fields.Char("Encounter No.", copy=False)
    encounter_id = fields.Many2one("ni.encounter", check_company=True, copy=False)
    department_id = fields.Many2one("hr.department", check_company=True)
    performer_id = fields.Many2one("hr.employee", check_company=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in-progress", "In-Progress"),
            ("finished", "Completed"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        default="draft",
    )

    @api.onchange("title")
    def _onchange_title(self):
        if self.title and self.title.gender:
            self.gender = self.title.gender

    @api.onchange("performer_id")
    def _onchange_performer_id(self):
        if self.performer_id and self.department_id != self.performer_id.department_id:
            self.department_id = self.performer_id.department_id

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            data = self.partner_id.copy_data({"name": self.partner_id.name})[0]
            vals = {key: val for key, val in data.items() if key in self._fields.keys()}
            vals["company_id"] = self.company_id.id
            patient_id = self.partner_id.patient_ids.filtered(
                lambda i: i.company_id == self.company_id
            )
            if patient_id:
                vals |= {
                    "patient_id": patient_id.id,
                    "identification_id": patient_id.identification_id,
                    "allergy_code_ids": [
                        fields.Command.set(patient_id.allergy_ids.code_id.ids)
                    ],
                    "condition_problem_ids": [
                        fields.Command.set(patient_id.condition_problem_ids.code_id.ids)
                    ],
                }
                if patient_id.encounter_id:
                    vals |= {
                        "body_height": patient_id.encounter_id.body_height,
                        "body_weight": patient_id.encounter_id.body_weight,
                    }
            else:
                vals |= {"patient_id": None}
            self.update(vals)
        else:
            self.patient_id = None

    def action_submit(self):
        self.ensure_one()
        if not self.patient_id and self.partner_id:
            # Try to find Patient ID if Partner ID present to make sure we're not creating duplicate Patient record
            self.patient_id = self.partner_id.patient_ids.filtered(
                lambda i: i.company_id == self.company_id
            )

        if not self.patient_id or self.patient_id.company_id != self.company_id:
            patient = self.env["ni.patient"].create(self.patient_data())
            self.patient_id = patient
            logging.info(
                "Created ni.patient[%d] with res.partner[%d]",
                self.patient_id.id,
                self.patient_id.partner_id.id,
            )
        if not self.patient_id:
            raise ValidationError(
                _("Create patient process went wrong, please contact administrator.")
            )

        data = self.encounter_data()
        if not self.encounter_id:
            enc = self.env["ni.encounter"].create(data)[0]
            self.write(
                {
                    "encounter_id": enc.id,
                    "encounter_identifier": enc.identifier,
                    "state": "in-progress",
                }
            )
        else:
            self.encounter_id.write(data[0])
        return {
            "name": self.encounter_id.identifier,
            "type": "ir.actions.act_window",
            "res_model": "ni.encounter",
            "res_id": self.encounter_id.id,
            "target": "current",
            "views": [[False, "form"]],
        }

    def _get_condition_data(self):
        patient_state = self.env.ref("ni_condition.class_patient_state")
        return [
            fields.Command.create(
                {
                    "code_id": c.id,
                    "class_id": patient_state.id,
                    "is_problem": True,
                }
            )
            for c in self.condition_problem_ids
        ]

    def patient_data(self):
        vals = self.copy_data(
            {"name": self.name, "condition_ids": self._get_condition_data()}
        )
        return [{k: v for k, v in d.items() if k in PATIENT_FIELD} for d in vals]

    def encounter_data(self):
        vals = self.copy_data({"identifier": self.encounter_identifier or "New"})
        return [{k: v for k, v in d.items() if k in ENCOUNTER_FIELD} for d in vals]
