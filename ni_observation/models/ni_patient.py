#  Copyright (c) 2021 NSTDA
import ast

from odoo import _, api, fields, models


class Patient(models.Model):
    _name = "ni.patient"
    _inherit = ["ni.patient", "ni.observation.bloodgroup.mixin"]

    @api.model
    def _get_default_observation_category(self):
        categ = self.env["ni.observation.category"].search(
            [("type_count", ">", 0)], limit=1
        )
        return categ.id

    observation_problem_only = fields.Boolean(
        default=False,
        store=False,
        help="Check here to display only the problem observations",
    )
    observation_category_id = fields.Many2one(
        "ni.observation.category",
        default=_get_default_observation_category,
        domain=[("type_count", ">", 0)],
        store=True,
    )
    observation_sheet_ids = fields.One2many(
        "ni.observation.sheet",
        "patient_id",
        domain=[("active", "=", True)],
        groups="ni_observation.group_user",
    )
    observation_sheet_count = fields.Integer(compute="_compute_observation_sheet_count")

    filtered_patient_observation_ids = fields.One2many(
        "ni.patient.observation", compute="_compute_display_patient_observation"
    )
    patient_observation_ids = fields.One2many("ni.patient.observation", "patient_id")

    @api.depends("observation_category_id", "observation_problem_only")
    def _compute_display_patient_observation(self):
        for rec in self:
            domain = [("category_id", "=", rec.observation_category_id.id)]
            if rec.observation_problem_only:
                domain += [("is_problem", "=", True)]

            rec.filtered_patient_observation_ids = (
                rec.patient_observation_ids.filtered_domain(domain)
            )

    def _compute_observation_sheet_count(self):
        observations = self.env["ni.observation.sheet"].sudo()
        read = observations.read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["patient_id"]
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in read}
        for patient in self:
            patient.observation_sheet_count = data.get(patient.id, 0)

    def action_observation(self):
        action_rec = self.env.ref("ni_observation.ni_observation_action").sudo()
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

    def _name_get(self):
        name = super(Patient, self)._name_get()
        if (
            self._context.get("show_gender_age")
            and (self.age or self.gender)
            and self.blood_group
        ):
            name = _("{} • Blood group {}").format(name, self.blood_group)
        return name

    def action_view_observation_sheet(self):
        self.ensure_one()
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            ._for_xml_id("ni_observation.ni_observation_sheet_action")
        )
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        context.update(
            {
                "create": self.active,
                "active_test": self.active,
                "default_patient_id": self.id,
            }
        )
        action["context"] = context
        action["domain"] = [("patient_id", "=", self.id)]
        return action
