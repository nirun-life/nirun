#  Copyright (c) 2024 NSTDA

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    @api.model
    def default_get(self, fields):
        res = super(Patient, self).default_get(fields)
        if "condition_categ_id" in fields and "condition_categ_id" not in res:
            categ = self.env["ni.condition.category"].search([], limit=1)
            if categ:
                res["condition_categ_id"] = categ.id
        return res

    need_ids = fields.Many2many("ni.need", "ni_patient_need", "patient_id", "need_id")
    need_count = fields.Integer(compute="_compute_need_count")

    user_city_ids = fields.Many2many(
        "res.city", store=False, default=lambda self: self.env.user.city_ids
    )

    @api.depends("need_ids")
    def _compute_need_count(self):
        for rec in self:
            rec.need_count = len(rec.need_ids)

    def action_patient_need(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_patient_id": self.id,
            }
        )
        view = {
            "name": "Need",
            "res_model": "ni.patient.need",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_mode": "list,form",
            "context": ctx,
        }
        return view

    family_count = fields.Integer("จำนวนสมาชิกในครอบครัว")
    family_relation = fields.Many2one("ni.family.relation", "ความสัมพันธ์ในครอบครัว")

    type_id = fields.Many2one("ni.patient.type", "ประเภทผู้สูงอายุ")
    type_decoration = fields.Selection(related="type_id.decoration")
    line = fields.Char("LINE ID")

    service_event_ids = fields.One2many(
        "ni.service.event", compute="_compute_service_event"
    )
    service_event_count = fields.Integer(compute="_compute_service_event")

    plan = fields.Text("แนวทางในการให้ความช่วยเหลือดูแล")
    careplan_ids = fields.One2many("ni.careplan", "patient_id")
    careplan_count = fields.Integer(compute="_compute_careplan_count")

    @api.depends("careplan_ids")
    def _compute_careplan_count(self):
        for rec in self:
            rec.careplan_count = len(rec.careplan_ids)

    plan_service_ids = fields.Many2many(
        "ni.service",
        "ni_patient_service_plan",
        "patient_id",
        "service_id",
        "แผนกิจกรรม",
    )
    risk_assessment_ids = fields.One2many("ni.risk.assessment", "patient_id")
    risk_assessment_id = fields.Many2one(
        "ni.risk.assessment", compute="_compute_risk_assessment", store=True
    )
    planned_all = fields.Boolean(related="risk_assessment_id.planned_all")
    actual_ratio = fields.Float(related="risk_assessment_id.actual_ratio")

    risk_assessment_count = fields.Integer(compute="_compute_risk_assessment")
    attend_event_id = fields.Many2many("ni.service.event", "ni_patient_service_attend")

    condition_categ_id = fields.Many2one(
        "ni.condition.category",
    )
    condition_other = fields.Char("ปัญหาอื่นๆ")
    allergy_other = fields.Char("แพ้ยาอาหารอื่นๆ")

    heal_progress = fields.Boolean(default=False, compute="_compute_category_progress")
    soci_progress = fields.Boolean(default=False, compute="_compute_category_progress")
    econ_progress = fields.Boolean(default=False, compute="_compute_category_progress")
    envi_progress = fields.Boolean(default=False, compute="_compute_category_progress")
    tech_progress = fields.Boolean(default=False, compute="_compute_category_progress")

    country_code = fields.Char(related="country_id.code", store=True, index=True)
    state_code = fields.Char(related="state_id.code", store=True, index=True)
    sub_district_code = fields.Char(
        compute="_compute_sub_district_code",
        inverse="_inverse_sub_district_code",
        store=True,
        index=True,
    )

    @api.depends("zip_id")
    def _compute_sub_district_code(self):
        for rec in self:
            if not rec.zip_id:
                rec.sub_district_code = None
                continue
            rec.sub_district_code = rec.zip_id.sub_district_code

    def _inverse_sub_district_code(self):
        for rec in self:
            zip = self.env["res.city.zip"].search(
                [("sub_district_code", "=", rec.sub_district_code)], limit=1
            )
            rec.zip_id = zip[0] if zip else None

    @api.depends("service_event_ids")
    def _compute_category_progress(self):
        for rec in self:
            val = {
                "heal_progress": False,
                "soci_progress": False,
                "econ_progress": False,
                "envi_progress": False,
                "tech_progress": False,
            }
            grp = self.env["ni.service.event"].read_group(
                [("plan_patient_ids", "=", rec.id)], ["count"], "service_category_id"
            )
            for g in grp:
                cat_id = self.env["ni.service.category"].browse(
                    g.get("service_category_id")[0]
                )
                f = "{}_progress".format(cat_id.code)
                if f in self._fields:
                    val[f] = bool(g.get("service_category_id_count"))
            rec.update(val)

    def action_view_service_event(self):
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            ._for_xml_id("ni_community_care.ni_service_event_action_from_patient")
        )
        context = {
            "create": self.active,
            "active_test": self.active,
            "default_plan_patient_ids": [fields.Command.set(self.ids)],
            "default_patient_type_id": self.type_id.id,
            "default_patient_id": self.patient_id.id,
        }
        action["view_mode"] = "kanban,calendar,tree,pivot,form"
        action["context"] = context
        return action

    def _compute_service_event(self):
        for rec in self:
            event = self.env["ni.service.event"].search(
                [("plan_patient_ids", "=", rec.id)], order="start desc"
            )
            rec.service_event_ids = event
            rec.service_event_count = len(event)

    @api.depends("risk_assessment_ids")
    def _compute_risk_assessment(self):
        for rec in self:
            rec.risk_assessment_count = len(rec.risk_assessment_ids)
            rec.risk_assessment_id = (
                rec.risk_assessment_ids[0] if rec.risk_assessment_ids else None
            )

    def action_risk(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_patient_id": self.id,
            }
        )
        view = {
            "name": "Risk Assessment",
            "res_model": "ni.risk.assessment",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_type": "form",
            "views": [[False, "form"]],
            "context": ctx,
        }
        return view

    def action_survey_subject(self):
        action_rec = self.env.ref("survey_subject.survey_subject_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_subject_ni_patient": self.id,
            }
        )
        action["context"] = ctx
        return action


class PatientType(models.Model):
    _name = "ni.patient.type"
    _inherit = "ni.coding"

    decoration = fields.Selection(
        [
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("muted", "Muted"),
        ],
        default="muted",
        required=True,
    )


class FamilyRelation(models.Model):
    _name = "ni.family.relation"
    _inherit = "ni.coding"
