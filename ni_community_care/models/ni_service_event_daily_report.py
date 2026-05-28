#  Copyright (c) 2024 Piruin P.


from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class ServiceEventDailyReport(models.Model):
    _name = "ni.service.event.daily.report"
    _inherit = ["ni.my.area.mixin"]
    _description = "Service Event Daily Report"
    _order = "service_date desc"
    _auto = False
    _rec_name = "employee_id"

    service_date = fields.Datetime("เริ่ม", readonly=True)
    employee_id = fields.Many2one("hr.employee", "ผู้บริบาล", readonly=True)
    state_id = fields.Many2one("res.country.state", "จังหวัด", readonly=True)
    city_id = fields.Many2one("res.city", "ตำบล", readonly=True)
    user_id = fields.Many2one("res.users", "บัญชีผู้ใช้", readonly=True)
    duration = fields.Float("ระยะเวลารวม", readonly=True, group_operator="avg")
    total_services = fields.Integer("ประเภทกิจกรรม", group_operator="avg")
    total_events = fields.Integer("จำนวนกิจกรรม", group_operator="avg")
    total_patients = fields.Integer("จำนวนผู้สูงอายุ", group_operator="avg")
    ma_7d_events = fields.Float(
        "จำนวนกิจกรรมเฉลี่ย 7 วัน",
        help="7 Days Moving Average ของทั้งระบบ",
        group_operator="avg",
    )
    ma_30d_events = fields.Float(
        "จำนวนกิจกรรมเฉลี่ย 30 วัน",
        help="30 Days Moving Average ของทั้งระบบ",
        group_operator="avg",
    )
    ma_7d_patients = fields.Float(
        "จำนวนผู้สูงอายุเฉลี่ย 7 วัน",
        help="7 Days Moving Average ของทั้งระบบ",
        group_operator="avg",
    )
    ma_30d_patients = fields.Float(
        "จำนวนผู้สูงอายุเฉลี่ย 30 วัน",
        help="30 Days Moving Average ของทั้งระบบ",
        group_operator="avg",
    )

    my_service = fields.Boolean(
        "รายการของฉัน", compute="_compute_my_service", search="_search_my_service"
    )

    @api.depends("employee_id")
    def _compute_my_service(self):
        for rec in self:
            rec.my_service = rec.employee_id.id == self.env.user.employee_id.id

    def _search_my_service(self, operator, operand):
        if operator == "=":
            return [
                (
                    "employee_id",
                    "=" if bool(operand) else "!=",
                    self.env.user.employee_id.id,
                )
            ]
        raise ValidationError(_("my_service support only '=', 'True' or 'False'"))

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            WITH daily_stats AS (
                SELECT
                    DATE(se.start) AS service_date,
                    se.employee_id,
                    MAX(se.user_id) as user_id,
                    COUNT(DISTINCT se.service_id) AS total_services,
                    COUNT(DISTINCT se.id) AS total_events,
                    COUNT(DISTINCT pe.ni_patient_id) AS total_patients,
                    SUM(se.duration) AS duration,
                    MAX(se.state_id) AS state_id,
                    MAX(se.city_id) AS city_id
                FROM ni_patient_ni_service_event_rel pe
                LEFT JOIN ni_service_event se ON pe.ni_service_event_id = se.id
                GROUP BY DATE(se.start), se.employee_id
            ),

            aggregated_totals AS (
                SELECT
                    service_date,
                    AVG(total_events) AS total_events_all,
                    AVG(total_patients) AS total_patients_all
                FROM daily_stats
                GROUP BY service_date
            ),

            moving_averages AS (
                SELECT
                    service_date,
                    AVG(total_events_all) OVER (
                        ORDER BY service_date
                        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                    ) AS ma_7d_events,
                    AVG(total_events_all) OVER (
                        ORDER BY service_date
                        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
                    ) AS ma_30d_events,
                    AVG(total_patients_all) OVER (
                        ORDER BY service_date
                        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                    ) AS ma_7d_patients,
                    AVG(total_patients_all) OVER (
                        ORDER BY service_date
                        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
                    ) AS ma_30d_patients
                FROM aggregated_totals
            )
            SELECT
                row_number() OVER (ORDER BY ds.service_date, ds.employee_id) AS id,
                ds.service_date,
                ds.employee_id,
                ds.state_id,
                ds.city_id,
                ds.duration,
                ds.total_services,
                ds.total_events,
                ds.total_patients,
                ma.ma_7d_events,
                ma.ma_30d_events,
                ma.ma_7d_patients,
                ma.ma_30d_patients
            FROM daily_stats ds
            LEFT JOIN moving_averages ma ON ds.service_date = ma.service_date
            ORDER BY ds.service_date, ds.employee_id
        )
        """
            % (self._table)
        )
