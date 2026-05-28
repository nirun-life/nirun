#  Copyright (c) 2024 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class ServiceEventReport(models.Model):
    _name = "ni.service.event.report"
    _inherit = ["ni.my.area.mixin"]
    _description = "Service Event Report"
    _order = "start desc"
    _auto = False
    _rec_name = "event_id"

    event_id = fields.Many2one("ni.service.event", readonly=True)
    start = fields.Datetime("เริ่ม", readonly=True)
    stop = fields.Datetime("หยุด", readonly=True)
    duration = fields.Float("ระยะเวลา", readonly=True)
    service_id = fields.Many2one("ni.service", "กิจกรรม", readonly=True)
    service_ids = fields.Many2many(
        "ni.service", "ni_service_event_rel", "event_id", "service_id", "กิจกรรม"
    )
    service_category_id = fields.Many2one("ni.service.category", "มิติ", readonly=True)
    service_category_ids = fields.Many2many(
        related="event_id.service_category_ids", readonly=True
    )
    outcome = fields.Html(related="event_id.outcome", readonly=True)
    location = fields.Char(related="event_id.location", string="สถานที่", readonly=True)
    patient_id = fields.Many2one("ni.patient", "ผู้สูงอายุ", readonly=True)
    patient_type_id = fields.Many2one(
        "ni.patient.type", "ประเภทผู้สูงอายุ", readonly=True
    )
    employee_id = fields.Many2one("hr.employee", "ผู้บริบาล", readonly=True)
    user_id = fields.Many2one("res.users", "บัญชีผู้ใช้", readonly=True)
    city_id = fields.Many2one("res.city", "ตำบล", readonly=True)
    state_id = fields.Many2one("res.country.state", "จังหวัด", readonly=True)
    image_1 = fields.Image(related="event_id.image_1")
    image_2 = fields.Image(related="event_id.image_2")
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
        readonly=True,
        group_operator="avg",
    )

    my_service = fields.Boolean(
        compute="_compute_my_service", search="_search_my_service"
    )

    def action_service_event(self):
        self.ensure_one()
        view = {
            "name": self.event_id.name,
            "res_model": "ni.service.event",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": self.event_id.id,
            "view_type": "form",
            "views": [[False, "form"]],
            "context": self.env.context,
        }
        return view

    @api.depends("user_id")
    def _compute_my_service(self):
        for rec in self:
            rec.my_service = rec.user_id.id == self.env.user.id

    def _search_my_service(self, operator, operand):
        if operator == "=":
            return [("user_id", "=" if bool(operand) else "!=", self.env.user.id)]
        raise ValidationError(_("my_service support only '=', 'True' or 'False'"))

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
                se.satisfaction_level,
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
            ("patient_type_id", "!=", False),
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
