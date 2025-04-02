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
    patient_type_id = fields.Many2one("ni.patient.type")

    outcome = fields.Html("ผลการให้ความช่วยเหลือ")
    outcome_id = fields.Many2one("ni.service.event.outcome", "ผลการให้ความช่วยเหลือ")

    service_category_id = fields.Many2one(store=True)

    prediction_id = fields.Many2one("ni.risk.assessment.prediction")
    plan_patient_ids = fields.Many2many(string="ผู้สูงอายุ")
    user_name = fields.Char(
        related="event_id.user_id.display_name",
        string="ชื่อ-นามสกุลผู้บริบาล",
        store=True,
    )
    user_id = fields.Many2one(
        string="ผู้บริบาล",
        related="event_id.user_id",
        group_operator="count_distinct",
        store=True,
    )
    my_service_event = fields.Boolean(
        compute="_compute_my_service_event", search="_search_my_service_event"
    )
    start = fields.Datetime(default=_get_default_trim_start)
    stop = fields.Datetime(default=_get_default_trim_stop)

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
            rec.my_service_event = rec.user_id == self.env.user.id

    def _search_my_service_event(self, operator, operand):
        if operator == "=" and bool(operand):
            return [("user_id", "=" if bool(operand) else "!=", self.env.user.id)]
        raise ValidationError(_("my_service support only '=', 'True' or 'False'"))

    @api.onchange("patient_type_id", "service_category_id")
    def _onchange_patient_type_id(self):
        for rec in self:
            rec.service_ids = None

        if self.patient_type_id:
            domain = [
                ("category_id", "=", self.service_category_id.id),
                "|",
                ("target_type_ids", "=", False),
                ("target_type_ids", "=", self.patient_type_id.id),
            ]
        else:
            domain = [("category_id", "=", self.service_category_id.id)]
        return {"domain": {"service_ids": domain}}

    @api.constrains("start")
    def _check_start_date(self):
        now = fields.Datetime.now()
        for rec in self:
            acceptable_date = now.date() - relativedelta(days=7)
            if rec.start.date() < acceptable_date:
                be_date = acceptable_date.replace(year=acceptable_date.year + 543)
                raise UserError(
                    _(
                        "บันทึกกิจกรรมย้อนหลังได้ไม่เกิน 7 วัน (วันที่ {})".format(
                            be_date
                        )
                    )
                )
            if rec.start.date() > now.date():
                raise UserError(_("ไม่สามารถบันทึกกิจกรรมล่วงหน้าได้"))
