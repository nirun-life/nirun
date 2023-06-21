#  Copyright (c) 2023 NSTDA
import base64

from odoo import api, fields, models
from odoo.modules.module import get_module_resource


class Reception(models.Model):
    _name = "ni.reception"
    _description = "Reception"
    _inherit = ["ni.identifier.mixin", "ni.observation.vitalsign.mixin", "image.mixin"]
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
    partner_id = fields.Many2one("res.partner", store=False)
    patient_id = fields.Many2one("ni.patient")
    patient_age = fields.Integer(related="patient_id.age")
    title = fields.Many2one("res.partner.title")
    name = fields.Char(copy=False)
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

    period_start = fields.Datetime(
        "Encounter Start", default=fields.datetime.now(), required=True
    )
    chief_complaint = fields.Text()
    class_id = fields.Many2one("ni.encounter.class", required=True)
    reason_ids = fields.Many2many(
        "ni.encounter.reason", "ni_reception_reason", "reception_id", "reason_id"
    )
    condition_problem_ids = fields.Many2many(
        "ni.condition.code",
        "ni_reception_condition",
        "reception_id",
        "code_id",
        "Problem List",
        copy=False,
    )
    allergy_code_ids = fields.Many2many(
        "ni.allergy.code",
        "ni_reception_allergy",
        "reception_id",
        "code_id",
        "Allergy",
        copy=False,
    )
    priority = fields.Selection(
        [
            ("routine", "Routine"),
            ("asap", "ASAP"),
            ("urgent", "Urgent"),
            ("stat", "STAT"),
        ],
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
    encounter_id = fields.Many2one("ni.encounter", copy=False)

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

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            data = self.partner_id.copy_data({"name": self.partner_id.name})[0]
            vals = {key: val for key, val in data.items() if key in self._fields.keys()}
            patient_id = self.partner_id.patient_id
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
            self.update(vals)
        else:
            self.patient_id = None

    def action_submit(self):
        if not self.patient_id:
            # Cause by delegation inheritance, we need to write into patient before we can write into encounter
            # Maybe it just cause be name field of encounter
            patient = self.env["ni.patient"].create({"name": self.name})
            self.patient_id = patient
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

    def encounter_data(self):
        vals = self.copy_data({"identifier": self.encounter_identifier or "New"})
        return vals
