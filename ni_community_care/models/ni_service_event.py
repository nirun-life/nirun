#  Copyright (c) 2024 NSTDA
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ServiceEvent(models.Model):
    _inherit = "ni.service.event"

    @api.model
    def _get_default_trim_start(self):
        now = fields.Datetime.now()
        if now.minute > 30:
            return now.replace(minute=30, second=0)
        else:
            return now.replace(minute=0, second=0)

    @api.model
    def _get_default_trim_stop(self):
        return self._get_default_trim_start() + timedelta(hours=1)

    @api.model
    def default_get(self, _fields):
        res = super(ServiceEvent, self).default_get(_fields)
        if "plan_patient_ids" in res:
            patient_ids = res["plan_patient_ids"][0][2]
            pat = self.env["ni.patient"].browse(patient_ids[0])
            if "patient_id" not in res and "patient_id" in _fields:
                res["patient_id"] = pat.id
            if "service_category_id" in res:
                categ = self.env["ni.service.category"].browse(
                    res["service_category_id"]
                )
                careplan = self.env["ni.careplan"].search(
                    [
                        ("patient_id", "in", patient_ids),
                        ("service_category_id", "=", categ.id),
                    ]
                )
                if careplan.service_ids:
                    res["service_ids"] = [fields.Command.set(careplan.service_ids.ids)]
            if "patient_type_id" not in res:
                res["patient_type_id"] = pat.type_id.id
            if "state_id" not in res and pat.state_id:
                res["state_id"] = pat.state_id.id
            if "city_id" not in res and pat.city_id:
                res["city_id"] = pat.city_id.id
        return res

    state_id = fields.Many2one(
        "res.country.state",
        compute="_compute_state_city",
        store=True,
        index=True,
        ondelete="restrict",
    )
    city_id = fields.Many2one(
        "res.city",
        compute="_compute_state_city",
        store=True,
        index=True,
        ondelete="restrict",
    )
    attendance_id = fields.Many2one(required=False)

    patient_id = fields.Many2one("ni.patient", store=False)
    patient_type_id = fields.Many2one("ni.patient.type", required=True, index=True)

    outcome = fields.Html("ผลการให้ความช่วยเหลือ")
    outcome_id = fields.Many2one("ni.service.event.outcome", "ผลการให้ความช่วยเหลือ")

    service_category_id = fields.Many2one(store=True, required=True)

    prediction_id = fields.Many2one("ni.risk.assessment.prediction")
    plan_patient_ids = fields.Many2many(string="ผู้สูงอายุ")
    user_id = fields.Many2one(
        string="ผู้บริบาล",
        related="event_id.user_id",
        group_operator="count_distinct",
        store=True,
        readonly=False,
        default=lambda self: self.env.uid,
    )
    employee_id = fields.Many2one(
        related="user_id.employee_id",
        store=True,
        index=True,
        group_operator="count_distinct",
    )
    my_service_event = fields.Boolean(
        compute="_compute_my_service_event", search="_search_my_service_event"
    )
    start = fields.Datetime(default=_get_default_trim_start)
    stop = fields.Datetime(default=_get_default_trim_stop)
    time_range = fields.Char(string="เวลา", compute="_compute_time_range", store=False)

    satisfaction_level = fields.Selection(
        [
            ("1", "น้อยที่สุด"),
            ("2", "น้อย"),
            ("3", "ปานกลาง"),
            ("4", "มาก"),
            ("5", "มากที่สุด"),
        ],
        string="ความพึงพอใจ",
        help="ระดับความพึงพอใจของผู้สูงอายุหลังจากที่ได้รับบริการ",
    )

    @api.depends("start", "stop")
    def _compute_time_range(self):
        for rec in self:
            if rec.start and rec.stop:
                # แปลงจาก UTC → local time ของ user
                start_local = fields.Datetime.context_timestamp(rec, rec.start)
                stop_local = fields.Datetime.context_timestamp(rec, rec.stop)

                start_str = start_local.strftime("%H:%M")
                stop_str = stop_local.strftime("%H:%M")
                rec.time_range = f"{start_str} - {stop_str}"
            else:
                rec.time_range = ""

    @api.depends("state_id", "city_id")
    def _compute_state_city(self):
        for rec in self:
            if rec.plan_patient_ids:
                patient = rec.plan_patient_ids[0]
                rec.update(
                    {"state_id": patient.state_id.id, "city_id": patient.city_id.id}
                )
            else:
                rec.update({"state_id": None, "city_id": None})

    @api.depends("user_id")
    def _compute_my_service_event(self):
        for rec in self:
            rec.my_service_event = rec.user_id == self.env.user

    def _search_my_service_event(self, operator, operand):
        if operator == "=":
            return [("user_id", "=" if bool(operand) else "!=", self.env.user.id)]
        raise ValidationError(_("my_service support only '=', 'True' or 'False'"))

    @api.onchange("service_id")
    def _onchange_service_id(self):
        saved_user = {rec: rec.user_id for rec in self}
        result = super()._onchange_service_id()
        for rec in self:
            rec.user_id = saved_user[rec]
        return result

    @api.onchange("patient_type_id", "service_category_id")
    def _onchange_patient_type_id(self):
        for rec in self:
            rec.service_ids = None

        if self.patient_type_id:
            domain = [
                "&",
                "&",
                ("category_id", "=", self.service_category_id.id),
                "|",
                ("target_type_ids", "=", False),
                ("target_type_ids", "=", self.patient_type_id.id),
                "|",
                ("user_id", "=", self.env.user.id),
                ("user_id", "=", False),
            ]
        else:
            domain = [
                "&",
                ("category_id", "=", self.service_category_id.id),
                "|",
                ("user_id", "=", self.env.user.id),
                ("user_id", "=", False),
            ]
        return {"domain": {"service_ids": domain}}

    @api.constrains("start")
    def _check_start_date(self):
        now = fields.Datetime.now()
        today = now.date()

        for rec in self:
            if not rec.start:
                continue

            company = rec.company_id
            start_date = rec.start.date()

            # ❌ ห้ามบันทึกล่วงหน้า
            if start_date > today:
                raise UserError(_("ไม่สามารถบันทึกกิจกรรมล่วงหน้าได้"))

            system_start = company.system_start_date
            limit_days = company.backdate_limit_days

            # -----------------------------
            # กรณีเปิดย้อนหลังทั้งหมด (limit = -1)
            # -----------------------------
            if limit_days < 0:
                if system_start and start_date < system_start:
                    be_date = system_start.replace(year=system_start.year + 543)
                    raise UserError(
                        _(
                            "ไม่สามารถบันทึกข้อมูลก่อนวันที่ {} ได้ เนื่องจากเป็นวันที่เริ่มต้นใช้งานระบบ".format(
                                be_date
                            )
                        )
                    )

            # -----------------------------
            # กรณีปกติ (จำกัดตามจำนวนวัน)
            # -----------------------------
            else:
                acceptable_date = today - relativedelta(days=limit_days or 7)

                if start_date < acceptable_date:
                    be_date = acceptable_date.replace(year=acceptable_date.year + 543)
                    raise UserError(
                        _(
                            "บันทึกกิจกรรมย้อนหลังได้ไม่เกิน {} วัน (วันที่ {})".format(
                                limit_days, be_date
                            )
                        )
                    )

    @api.constrains("user_id", "partner_ids")
    def _check_user_partner(self):
        # The base implementation writes partner_ids inside a @api.constrains that
        # also watches partner_ids, causing infinite recursion.  The context flag
        # prevents re-entry so the write is idempotent and safe.
        if self.env.context.get("_in_check_user_partner"):
            return
        for rec in self.with_context(_in_check_user_partner=True):
            if not rec.user_id:
                continue
            if rec.user_id.partner_id and rec.user_id.partner_id not in rec.partner_ids:
                rec.partner_ids = [fields.Command.link(rec.user_id.partner_id.id)]

    @api.constrains("user_id", "employee_id")
    def _check_employee_id(self):
        for rec in self.filtered(lambda s: not s.employee_id):
            if rec.user_id.employee_id:
                rec.employee_id = rec.user_id.employee_id
                continue
            hr = self.env["hr.employee"].search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("user_id", "=", rec.user_id.id),
                ],
                limit=1,
            )
            if hr:
                rec.employee_id = hr
                continue

    @api.constrains("service_id", "service_ids", "mode")
    def _check_service_name(self):
        super()._check_service_name()
        # Truncate the auto-generated name so kanban cards and calendar chips stay
        # readable when many services are selected.  More than two names are
        # summarised as "A, B (+N)".
        for rec in self:
            if rec.service_count > 2:
                first_two = rec.service_ids[:2].mapped("name")
                rec.name = ", ".join(first_two) + f" (+{rec.service_count - 2})"

    @api.depends("image_1", "image_2")
    def _compute_attachment_ids(self):
        # fields.Image() stores data inline (no ir.attachment), so the base
        # implementation never sets has_image when only image_1/image_2 are used.
        # Extend it so the kanban card correctly shows the uploaded image.
        super()._compute_attachment_ids()
        for rec in self:
            if not rec.has_image and (rec.image_1 or rec.image_2):
                rec.has_image = True
