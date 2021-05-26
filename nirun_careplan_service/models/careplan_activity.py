#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Activity(models.Model):
    _inherit = "ni.careplan.activity"

    service_request_id = fields.Many2one("ni.service.request", "Relate Service")

    @api.onchange("service_request_id")
    def _onchange_service_request(self):
        for rec in self:
            if rec.service_request_id:
                rec.name = rec.service_request_id.service_id.name
                rec.period_start = rec.service_request_id.period_start
                rec.period_end = rec.service_request_id.period_end

    def write(self, vals):
        result = super(Activity, self).write(vals)

        if vals.get("service_request_id"):
            service_requests = self.env["ni.service.request"].sudo()
            sr = service_requests.browse(vals.get("service_request_id"))
            sr.write({"careplan_activity_id": self.ids[0]})

        return result
