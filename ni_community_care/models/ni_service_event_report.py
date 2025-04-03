#  Copyright (c) 2022 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class ServiceEventReport(models.Model):
    _name = "ni.service.event.report"
    _description = "Service Event Report"
    _order = "start desc"
    _auto = False
    _rec_name = "event_id"

    event_id = fields.Many2one("ni.service.event")
    start = fields.Datetime("เริ่ม")
    stop = fields.Datetime("หยุด")
    duration = fields.Float("ระยะเวลา")
    service_id = fields.Many2one("ni.service", "กิจกรรม")
    service_ids = fields.Many2many(
        "ni.service", "ni_service_event_rel", "event_id", "service_id", "กิจกรรม"
    )
    service_category_id = fields.Many2one("ni.service.category", "มิติ")
    outcome = fields.Html(related="event_id.outcome")
    location = fields.Char(related="event_id.location", string="สถานที่")
    patient_id = fields.Many2one("ni.patient", "ผู้สูงอายุ")
    patient_type_id = fields.Many2one("ni.patient.type", "ประเภทผู้สูงอายุ")
    employee_id = fields.Many2one("hr.employee", "ผู้บริบาล")
    user_id = fields.Many2one("res.users", "บัญชีผู้ใช้")
    city_id = fields.Many2one("res.city", "ตำบล")
    state_id = fields.Many2one("res.country.state", "จังหวัด")
    image_1 = fields.Image(related="event_id.image_1")
    image_2 = fields.Image(related="event_id.image_2")

    my_service = fields.Boolean(
        compute="_compute_my_service", search="_search_my_service"
    )
    my_area = fields.Boolean(compute="_compute_my_area", search="_search_my_area")

    @api.depends("user_id")
    def _compute_my_service(self):
        for rec in self:
            rec.my_service = rec.user_id == self.env.user.id

    def _search_my_service(self, operator, operand):
        if operator == "=" and bool(operand):
            return [("user_id", "=" if bool(operand) else "!=", self.env.user.id)]
        raise ValidationError(_("my_service support only '=', 'True' or 'False'"))

    @api.depends("city_id")
    def _compute_my_area(self):
        for rec in self:
            rec.my_area = rec.city_id.id in self.env.user.city_ids.ids

    def _search_my_area(self, operator, operand):
        if operator == "=" and bool(operand):
            if self.user_has_groups("ni_patient.group_manager"):
                return [
                    (
                        "state_id",
                        "in" if bool(operand) else "not in",
                        self.env.user.state_ids.ids,
                    )
                ]
            return [
                (
                    "city_id",
                    "in" if bool(operand) else "not in",
                    self.env.user.city_ids.ids,
                )
            ]
        raise ValidationError(_("my_area support only '=', 'True' or 'False'"))

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT
                pe.ni_service_event_id as id,
                se.id as event_id,
                se.service_id,
                se.service_category_id,
                se.start,
                se.stop,
                se.duration,
                pat.type_id as patient_type_id,
                pe.ni_patient_id as patient_id,
                se.user_id,
                se.employee_id,
                se.state_id,
                se.city_id
            FROM ni_patient_ni_service_event_rel pe
                LEFT JOIN ni_service_event se ON pe.ni_service_event_id = se.id
                LEFT JOIN ni_patient pat ON pe.ni_patient_id = pat.id
            WHERE se.patient_type_id IS NOT NULL
        )
        """
            % (self._table)
        )

    @api.model
    def get_patient_type_dashboard(self):
        res = {
            "adl-high": {
                "description": _("ติดสังคม"),
                "amount": 0,
                "target": 0,
                "class": "text-success",
                "icon": "fa-comments",
            },
            "adl-mid": {
                "description": _("ติดบ้าน"),
                "amount": 0,
                "target": 0,
                "class": "text-odoo",
                "icon": "fa-home",
            },
            "adl-low": {
                "description": _("ติดเตียง"),
                "amount": 0,
                "target": 0,
                "class": "text-danger",
                "icon": "fa-bed",
            },
        }
        today = fields.Date.today()
        this_month = (today + relativedelta(months=0)).strftime("%Y-%m-01")
        next_month = (today + relativedelta(months=1)).strftime("%Y-%m-01")

        patient_types = self.env["ni.patient.type"]
        patient_type_map = {pt.id: pt for pt in patient_types.search([])}
        for rec in patient_type_map.values():
            if rec.code in res:
                res[rec.code]["target"] = rec.target
        domain = [
            ("start", ">=", this_month),
            ("start", "<", next_month),
        ]
        if self.user_has_groups("ni_patient.group_manager"):
            domain += [("my_area", "=", True)]
        elif self.user_has_groups("ni_patient.group_user"):
            domain += [("user_id", "=", self.env.user.id)]
        # observer will see all
        datas = self.read_group(
            domain,
            ["patient_type_id", "patient_id:count_distinct"],
            ["patient_type_id"],
        )
        for data in datas:
            patient_type = patient_type_map.get(data["patient_type_id"][0])
            if patient_type.code in res:
                res[patient_type.code]["amount"] += data["patient_id"]
        return res
