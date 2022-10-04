#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class Meeting(models.Model):
    _inherit = "calendar.event"

    service_id = fields.Many2one("ni.service", ondelete="cascade")
    timing_id = fields.Many2one(
        "ni.service.timing",
        domain="[('service_id', '=', service_id)]",
        ondelete="cascade",
    )
    time_id = fields.Many2one(
        "ni.service.time",
        domain="[('service_id', '=', service_id)]",
        ondelete="cascade",
    )
    # To support recurrence event, We have to compute with _read_service_request_ids()
    service_request_ids = fields.Many2many(
        "ni.service.request", readonly=True, default=False
    )
    patient_ids = fields.Many2many("ni.patient", readonly=True, default=False)
    patient_count = fields.Integer(readonly=True, default=0)
    encounter_ids = fields.Many2many("ni.encounter", readonly=True, default=False)

    @api.onchange("service_id")
    def onchange_service_id(self):
        service_tag = self.env.ref("nirun_service_calendar.calendar_categ_service")
        for rec in self:
            if rec.service_id:
                rec.res_model = "ni.service"
                rec.res_id = rec.service_id.id
                rec.categ_ids = [(4, service_tag.id)]
            else:
                rec.res_model = None
                rec.res_id = None
                rec.categ_ids = [(3, service_tag.id)]

    def read(self, fields=None, load="_classic_read"):
        result = super(Meeting, self).read(fields, load)
        if "service_request_ids" in fields or "patient_ids" in fields:
            result = self._read_service_request_ids(result)
        return result

    def _read_service_request_ids(self, data):
        result = []
        for d in data:
            require_key = True
            for key in ["service_id", "start", "stop", "timing_id", "time_id"]:
                if key not in d:
                    require_key = False
            if not require_key:
                break
            if not d["service_id"]:
                result.append(d)
                continue
            domain = [
                ("service_id", "=", d["service_id"][0]),
                ("period_start", "<=", d["start"]),
                "|",
                ("period_end", ">=", d["stop"]),
                ("period_end", "=", False),
                ("state", "=", "active"),
            ]
            if d["timing_id"]:
                domain.insert(1, ("service_timing_id", "=", d["timing_id"][0]))
            if d["time_id"]:
                domain.insert(1, ("service_time_id", "=", d["time_id"][0]))

            res = d.copy()
            sr = self.env["ni.service.request"].search(domain)
            res["service_request_ids"] = sr.ids
            patients = sr.mapped("patient_id")
            res["patient_ids"] = patients.ids
            res["patient_count"] = len(patients)
            res["encounter_ids"] = sr.mapped("encounter_id").ids
            result.append(res)
        return result

    def action_procedure(self):
        action_rec = self.env.ref("nirun_service.service_request_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_calendar_id": self.ids[0],
                "default_service_id": self.service_id.id,
                "default_service_timing_id": self.timing_id.id,
                "default_service_time_id": self.time_id.id,
                "no_state_control": True,
            }
        )
        action["context"] = ctx
        action["name"] = "{} ({})".format(self.name, self.start)
        domain = [
            ("service_id", "=", self.service_id.id),
            ("period_start", "<=", self.start),
            "|",
            ("period_end", ">=", self.stop),
            ("period_end", "=", False),
            ("state", "=", "active"),
        ]
        if self.timing_id:
            domain.insert(1, ("service_timing_id", "=", self.timing_id.id))
        if self.time_id:
            domain.insert(1, ("service_time_id", "=", self.time_id.id))
        action["domain"] = domain
        return action
