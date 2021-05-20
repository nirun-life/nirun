#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Activity(models.Model):
    _inherit = "ni.careplan.activity"

    service_req_id = fields.Many2one("ni.service.request", "Relate Service")

    @api.onchange("service_req_id")
    def _onchange_service_request(self):
        for rec in self:
            if rec.service_req_id:
                rec.name = rec.service_req_id.service_id.name
                rec.period_start = rec.service_req_id.period_start
                rec.period_end = rec.service_req_id.period_end
