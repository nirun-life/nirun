#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Meeting(models.Model):
    _inherit = "calendar.event"

    service_id = fields.Many2one("ni.service", ondelete="set null")

    @api.onchange("service_id")
    def onchange_service_id(self):
        service_tag = self.env.ref("nirun_calendar.calendar_categ_service")
        for rec in self:
            if rec.service_id:
                rec.res_model = "ni.service"
                rec.res_id = rec.service_id.id
                rec.categ_ids = [(4, service_tag.id)]
            else:
                rec.res_model = None
                rec.res_id = None
                rec.categ_ids = [(3, service_tag.id)]
