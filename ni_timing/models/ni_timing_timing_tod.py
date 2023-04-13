#  Copyright (c) 2021-2023 NSTDA

import math

import pytz

from odoo import _, api, fields, models


def float_time_convert(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    return factor * int(math.floor(val)), int(round((val % 1) * 60))


def float_time_format(float_val):
    h, m = float_time_convert(float_val)
    return "%0d:%02d" % (h, m)


def _tz_get(self):
    return [
        (tz, tz)
        for tz in sorted(
            pytz.all_timezones, key=lambda tz: tz if not tz.startswith("Etc/") else "_"
        )
    ]


class TimingTimeOfDay(models.Model):
    _name = "ni.timing.timing.tod"
    _description = "Time of Day"
    timing_id = fields.Many2one("ni.timing.timing", ondelete="cascade")

    name = fields.Char(store=True, compute="_compute_name")
    code_id = fields.Many2one("ni.timing.tod", store=False)
    all_day = fields.Boolean()
    start_time = fields.Float()
    end_time = fields.Float()
    tz = fields.Selection(
        _tz_get, string="Timezone", default=lambda self: self._context.get("tz")
    )
    start = fields.Char(compute="_compute_start_end")
    end = fields.Char(compute="_compute_start_end")

    @api.depends("start_time", "end_time")
    def _compute_start_end(self):
        for rec in self:
            rec.start = float_time_format(rec.start_time)
            rec.end = float_time_format(rec.end_time)

    @api.onchange("all_day", "start_time", "end_time")
    @api.depends("all_day", "start_time", "end_time")
    def _compute_name(self):
        for rec in self:
            if rec.all_day:
                rec.name = _("24 hrs")
                continue
            res = []
            if rec.start_time:
                res.append(rec.start)
                if rec.end_time:
                    res.append(rec.end)
            rec.name = "-".join(res).strip()

    @api.onchange("code_id")
    def onchange_code_id(self):
        if self.code_id:
            data = self.code_id.copy_data()[0]
            field = ["all_day", "start_time", "end_time"]
            self.write({f: data[f] for f in field})
