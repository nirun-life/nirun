#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Activity(models.Model):
    _inherit = "ni.careplan.activity"

    service_request_id = fields.Many2one(
        "ni.service.request", "Relate Service", tracking=True, check_company=True
    )

    @api.onchange("service_request_id")
    def _onchange_service_request(self):
        for rec in self:
            if rec.service_request_id:
                rec.name = rec.service_request_id.service_id.name
                rec.period_start = rec.service_request_id.period_start
                rec.period_end = rec.service_request_id.period_end
                if rec.service_request_id.category_ids:
                    rec.category_id = rec.service_request_id.category_ids[
                        0
                    ].careplan_category_id

    @api.model
    def create(self, vals):
        activity = super().create(vals)

        if vals.get("service_request_id"):
            activity._link_with_request(vals)

        return activity

    def write(self, vals):
        result = super(Activity, self).write(vals)

        if vals.get("service_request_id"):
            self._link_with_request(vals)

        return result

    def _link_with_request(self, vals):
        requests = self.env["ni.service.request"].sudo()
        request = requests.browse(vals.get("service_request_id"))
        return request.write({"careplan_activity_id": self.ids[0]})
