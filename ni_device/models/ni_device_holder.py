from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class DeviceHolder(models.Model):
    _name = "ni.device.holder"
    _description = "Device Holder History"
    _order = "create_date DESC"
    _inherit = ["ni.holder.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_id = fields.Many2one(
        "ni.device", string="Device", check_company=True, index=True, required=True
    )
    device_identifier = fields.Char(
        related="device_id.identifier", string="Device Identifier"
    )
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date")

    request_id = fields.Many2one("ni.device.request", string="Related Request")

    display_duration = fields.Char(
        string="Duration",
        compute="_compute_duration",
        store=False,
    )

    # เก็บจำนวนวัน (ไว้ใช้ business / report)
    duration_days = fields.Integer(
        string="Duration (Days)",
        compute="_compute_duration",
        store=False,
    )

    @api.depends("start_date", "end_date")
    def _compute_duration(self):
        today = fields.Date.context_today(self)

        for rec in self:
            rec.duration_days = 0
            rec.display_duration = None

            if not rec.start_date:
                continue

            start = fields.Datetime.to_datetime(rec.start_date).date()

            end = rec.end_date or today
            if hasattr(end, "date"):
                end = end.date()

            # ---- duration_days (business) ----
            rec.duration_days = (end - start).days

            # ---- display (relativedelta + inclusive) ----
            rd = relativedelta(end, start)

            rec.display_duration = self._format_duration(rd)

    @api.model
    def _format_duration(self, delta):
        result = []
        if delta.years > 0:
            result.append(_("%s Years") % delta.years)
        if delta.months > 0:
            result.append(_("%s Months") % delta.months)
        if delta.days > 1:
            result.append(_("%s Days") % delta.days)
        else:
            result.append(_("%s Day") % delta.days)
        return " ".join(result)
