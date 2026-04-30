#  Copyright (c) 2024 NSTDA

from dateutil.relativedelta import relativedelta

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class Patient(models.Model):
    _inherit = "ni.patient"

    @api.model
    def default_get(self, _fields):
        res = super(Patient, self).default_get(_fields)
        if "condition_categ_id" in _fields and "condition_categ_id" not in res:
            categ = self.env["ni.condition.category"].search([], limit=1)
            if categ:
                res["condition_categ_id"] = categ.id
        return res

    observation_category_id = fields.Many2one(store=True)

    coverage_type_id = fields.Many2one("ni.coverage.type")

    need_ids = fields.Many2many("ni.need", "ni_patient_need", "patient_id", "need_id")
    need_line_ids = fields.One2many("ni.patient.need.line", "patient_id")
    need_count = fields.Integer(compute="_compute_need_count")
    need_other = fields.Char("ความต้องการอื่นๆ")

    relative_benefit_ids = fields.Many2many(
        "ni.relative.benefit",
        "ni_paitient_relative_benefit",
        "patient_id",
        "relative_benefit_id",
    )

    living_with_ids = fields.Many2many(
        "ni.living.with", "ni_patient_living_with", "patient_id", "living_with_id"
    )
    living_with_other = fields.Char("อื่นๆ ระบุ")

    user_city_ids = fields.Many2many(
        "res.city", store=False, default=lambda self: self.env.user.city_ids
    )

    is_accept_service = fields.Boolean(
        string="ยินยอมรับบริการจากผู้บริบาลคุ้มครองสิทธิผู้สูงอายุ"
    )
    is_allow_photo = fields.Boolean(string="ยินยอมให้ถ่ายภาพระหว่างให้บริการ")

    relative_benefit_count = fields.Integer(compute="_compute_relative_benefit_count")

    chronic_disease = fields.Selection(
        [
            ("none", "ไม่มีโรคประจำตัว"),
            ("has", "มีโรคประจำตัว"),
        ],
        string="โรคประจำตัว",
        required=True,
        default="none",
    )
    chronic_disease_detail = fields.Char(
        string="ระบุโรค", help="เช่น เบาหวาน, ความดันโลหิตสูง"
    )

    register_date_editable = fields.Boolean(related="company_id.register_date_editable")
    register_date_change = fields.Boolean("แก้ไขวันที่ขึ้นทะเบียน")
    register_date = fields.Datetime("วันที่ขึ้นทะเบียน")

    @api.onchange("register_date_change")
    def _onchange_register_date_change(self):
        for rec in self:
            if rec.register_date_change and not rec.register_date:
                rec.register_date = fields.Datetime.now()
            if not rec.register_date_change:
                rec.register_date = rec.create_date or None

    @api.constrains("register_date", "register_date_change")
    def _check_register_date(self):
        now = fields.Datetime.now()
        company = self.env.company
        system_start = company.system_start_date
        limit = company.backdate_limit_days

        for rec in self.filtered("register_date"):
            if not rec.register_date_change:
                if rec.register_date != rec.create_date:
                    rec.register_date = rec.create_date
                continue

            be_regis_date = rec.register_date.replace(year=rec.register_date.year + 543)
            if rec.register_date > now:
                raise UserError(
                    _(
                        f"วันที่ขึ้นทะเบียน [{be_regis_date}] ต้องไม่เกินกว่าวันเวลาปัจจุบัน {now}"
                    )
                )

            if limit < 0:
                if system_start and rec.register_date < system_start:
                    be_date = system_start.replace(year=system_start.year + 543)
                    raise UserError(
                        _(
                            f"ไม่สามารถบันทึกวันที่ขึ้นทะเบียน [{be_regis_date}] ก่อนวันที่ {be_date} ได้"
                        )
                    )
            else:
                acceptable_date = rec.create_date.date() - relativedelta(
                    days=limit or 7
                )
                if rec.register_date.date() < acceptable_date:
                    be_date = acceptable_date.replace(year=acceptable_date.year + 543)
                    be_create = rec.create_date.date().replace(
                        year=rec.create_date.year + 543
                    )
                    raise UserError(
                        _(
                            f"สามารถวันที่ขึ้นทะเบียน [{be_regis_date}] ย้อนหลังได้ไม่เกิน {limit} วัน "
                            f"จากวันที่บันทึกข้อมูล (วันที่ {be_date} ถึง {be_create})"
                        )
                    )

    def _update_register_date(self, limit=3000):
        patients = self.search([("register_date", "=", False)], limit=3000)
        for patient in patients:
            patient.register_date = patient.create_date

    @api.onchange("chronic_disease")
    def _onchange_chronic_disease(self):
        if self.chronic_disease != "has":
            self.chronic_disease_detail = False

    @api.depends("relative_benefit_ids")
    def _compute_relative_benefit_count(self):
        for rec in self:
            rec.relative_benefit_count = len(rec.relative_benefit_ids)

    # ---------------------------------------------------
    #  Onchange birthdate
    # ---------------------------------------------------
    @api.onchange("birthdate")
    def _onchange_birthdate_warn(self):
        for rec in self:
            if rec.birthdate:
                rec.partner_id.birthdate = rec.birthdate

    # ---------------------------------------------------
    #  Onchange age (ถ้าแก้ไขอายุโดยตรง)
    # ---------------------------------------------------
    @api.onchange("age")
    def _onchange_age_warn(self):
        for rec in self:
            # ถ้ายังไม่บันทึก (create mode) -> rec.id ไม่มี
            if not rec.id:
                return

            if rec.age >= 0 and rec.age < 60:
                return {
                    "warning": {
                        "title": _("อายุน้อยกว่า 60 ปี"),
                        "message": _(
                            "ไม่สามารถบันทึกข้อมูลได้ เนื่องจากอายุน้อยกว่า 60 ปี"
                        ),
                    }
                }

    # ---------------------------------------------------
    # 3️⃣ Constrains ก่อน save
    # ---------------------------------------------------
    @api.constrains("birthdate", "age")
    def _check_age_limit(self):
        for rec in self:
            age = rec.age or 0
            if age < 60:
                raise ValidationError(
                    _("ไม่สามารถบันทึกข้อมูลได้ เนื่องจากอายุน้อยกว่า 60 ปี")
                )

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [
            dict(vals, need_line_ids=self._need_line_values(vals.get("need_ids")))
            if not vals.get("need_line_ids")
            else vals
            for vals in vals_list
        ]
        for vals in vals_list:
            if "register_date" not in vals:
                vals["register_date"] = fields.Datetime.now()
        return super(Patient, self).create(vals_list)

    def write(self, vals):
        if "need_ids" in vals:
            vals["need_line_ids"] = self._need_line_values(vals["need_ids"])
        # age is computed from birthdate; strip it when birthdate is being written
        # to prevent age_mixin.write from clearing birthdate in a separate partner write
        if vals.get("birthdate") and "age" in vals:
            vals = {k: v for k, v in vals.items() if k != "age"}
        return super(Patient, self).write(vals)

    def _need_line_values(self, need_commands):
        """
        :param need_commands: ORM commands for partner_id field (0 and 1 commands not supported)
        :return: associated attendee_ids ORM commands
        """
        need_line_commands = []

        removed_need_ids = []
        added_need_ids = []

        # if commands are just integers, assume they are ids with the intent to `Command.set`
        if need_commands and isinstance(need_commands[0], int):
            need_commands = [Command.set(need_commands)]

        for command in need_commands:
            op = command[0]
            if op in (2, 3, Command.delete, Command.unlink):  # Remove partner
                removed_need_ids += [command[1]]
            elif op in (6, Command.set):  # Replace all
                removed_need_ids += set(self.need_ids.ids) - set(
                    command[2]
                )  # Don't recreate attendee if partner already attend the event
                added_need_ids += set(command[2]) - set(self.need_ids.ids)
            elif op in (4, Command.link):
                added_need_ids += (
                    [command[1]] if command[1] not in self.need_ids.ids else []
                )
            # commands 0 and 1 not supported

        if not self:
            attendees_to_unlink = self.env["ni.patient.need.line"]
        else:
            attendees_to_unlink = self.env["ni.patient.need.line"].search(
                [
                    ("patient_id", "in", self.ids),
                    ("need_id", "in", removed_need_ids),
                ]
            )
        need_line_commands += [
            [2, attendee.id] for attendee in attendees_to_unlink
        ]  # Removes and delete

        need_line_commands += [
            [0, 0, dict(need_id=need_id)] for need_id in added_need_ids
        ]
        return need_line_commands

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
            "res_model": "ni.patient.need.line",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_mode": "list,form",
            "context": ctx,
            "domain": [("patient_id", "=", self.id)],
        }
        return view

    family_count = fields.Integer("จำนวนสมาชิกในครอบครัว")
    family_relation = fields.Many2one("ni.family.relation", "ความสัมพันธ์ในครอบครัว")

    type_id = fields.Many2one("ni.patient.type", "ประเภทผู้สูงอายุ")
    type_name = fields.Char(related="type_id.name")
    type_decoration = fields.Selection(
        related="type_id.decoration",
        string="Type Decoration",
    )
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

    age_range_id = fields.Many2one(
        related="partner_id.age_range_id", store=True, index=True
    )
    country_code = fields.Char(related="country_id.code", store=True, index=True)
    state_id = fields.Many2one(
        related="partner_id.state_id", store=True, index=True, readonly=False
    )
    state_code = fields.Char(related="partner_id.state_id.code", store=True, index=True)
    city_id = fields.Many2one(
        related="partner_id.city_id", store=True, index=True, readonly=True
    )
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
            city_zip = self.env["res.city.zip"].search(
                [("sub_district_code", "=", rec.sub_district_code)], limit=1
            )
            rec.zip_id = city_zip[0] if city_zip else None

    @api.depends("service_event_ids")
    def _compute_category_progress(self):
        today = fields.Date.today()
        this_month = (today + relativedelta(months=0)).strftime("%Y-%m-01")
        next_month = (today + relativedelta(months=1)).strftime("%Y-%m-01")

        # Fetch all relevant data in one query
        grp = self.env["ni.service.event"].read_group(
            [
                ("plan_patient_ids", "in", self.ids),
                ("start", ">=", this_month),
                ("start", "<", next_month),
                ("service_category_id", "!=", False),
            ],
            ["plan_patient_ids", "service_category_id", "count"],
            ["plan_patient_ids", "service_category_id"],
            lazy=False,
        )

        # Map results for quick access
        progress_map = {}
        for g in grp:
            plan_id = g.get("plan_patient_ids")[0]  # Extract record ID
            cat_id = g.get("service_category_id")[0]
            count = g.get("__count", 0)
            progress_map.setdefault(plan_id, {})[cat_id] = bool(count)

        # Process records using cached results
        category_fields = {
            "heal_progress": False,
            "soci_progress": False,
            "econ_progress": False,
            "envi_progress": False,
            "tech_progress": False,
        }
        for rec in self:
            val = category_fields.copy()  # Start with all fields set to False
            if rec.id in progress_map:
                for cat_id, has_count in progress_map[rec.id].items():
                    cat = self.env["ni.service.category"].browse(cat_id)
                    field = f"{cat.code}_progress"
                    if field in category_fields:
                        val[field] = has_count
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

    @api.model
    def get_patient_type_dashboard(self):
        patient_type_status = {
            "adl-no": {
                "description": _("รอการประเมิน"),
                "amount": 0,
                "class": "text-info",
            },
            "adl-high": {
                "description": _("ติดสังคม"),
                "amount": 0,
                "class": "text-success",
            },
            "adl-mid": {"description": _("ติดบ้าน"), "amount": 0, "class": "text-odoo"},
            "adl-low": {
                "description": _("ติดเตียง"),
                "amount": 0,
                "class": "text-danger",
            },
        }
        patient_type = self.read_group(
            [("deceased", "=", False)], ["type_id"], ["type_id"], lazy=False
        )
        pt = self.env["ni.patient.type"]
        for t in patient_type:
            if not t["type_id"]:
                patient_type_status["adl-no"]["amount"] += t["__count"]
                continue
            patient_type_status[pt.browse(t["type_id"][0]).code]["amount"] += t[
                "__count"
            ]
        return patient_type_status


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
    target = fields.Integer("จำนวนเป้าหมาย")


class FamilyRelation(models.Model):
    _name = "ni.family.relation"
    _inherit = "ni.coding"
