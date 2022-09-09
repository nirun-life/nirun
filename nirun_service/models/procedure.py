#  Copyright (c) 2022. NSTDA
from odoo import api, fields, models


class Procedure(models.Model):
    _inherit = "ni.procedure"

    service_request_id = fields.Many2one("ni.service.request", tracking=1)

    @api.onchange("service_request_id")
    def _onchange_service_request_id(self):
        for rec in self:
            if rec.service_request_id:
                rec.code_id = rec.service_request_id.procedure_code_id
