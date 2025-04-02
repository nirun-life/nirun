#  Copyright (c) 2022 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, tools


class ServiceEventReport(models.Model):
    _name = "ni.service.event.report"
    _description = "Service Event Report"
    _auto = False

    name = fields.Char("ชื่อกิจกรรม")
    event_id = fields.Many2one("calendar.event")
    start = fields.Datetime()
    stop = fields.Datetime()
    duration = fields.Float("ระยะเวลา")
    service_id = fields.Many2one("ni.service", "กิจกรรม")
    service_ids = fields.Many2many(
        "ni.service", "ni_service_event_rel", "event_id", "service_id", "กิจกรรม"
    )
    patient_id = fields.Many2one("ni.patient", "ผู้สูงอายุ")
    patient_type_id = fields.Many2one("ni.patient.type", "ประเภทผู้สูงอายุ")
    user_id = fields.Many2one("res.users", "บัญชีผู้บริบาล")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT
                pe.ni_service_event_id as id,
                se.id as event_id,
                c.name,
                se.service_id,
                se.start,
                se.stop,
                se.duration,
                pat.type_id as patient_type_id,
                pe.ni_patient_id as patient_id,
                c.user_id
            FROM ni_patient_ni_service_event_rel pe
            LEFT JOIN ni_service_event se ON pe.ni_service_event_id = se.id
            LEFT JOIN calendar_event c ON se.event_id = c.id
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

        datas = self.read_group(
            [
                ("start", ">=", this_month),
                ("start", "<", next_month),
                ("user_id", "=", self.env.user.id),
            ],
            ["patient_type_id", "patient_id:count_distinct"],
            ["patient_type_id"],
        )
        for data in datas:
            patient_type = patient_type_map.get(data["patient_type_id"][0])
            if patient_type.code in res:
                res[patient_type.code]["amount"] += data["patient_id"]
        return res
