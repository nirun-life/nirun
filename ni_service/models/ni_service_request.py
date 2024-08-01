#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ServiceRequest(models.Model):
    _name = "ni.service.request"
    _description = "Service Request"
    _inherit = ["ni.workflow.request.mixin", "ni.timing.mixin"]

    name = fields.Char("Service")
    category_id = fields.Many2one("ni.service.category")
    service_ids = fields.Many2many(
        "ni.service",
        "ni_service_request_service",
        "request_id",
        "service_id",
        check_company=True,
        domain="[('category_id', '=?', category_id),"
        " '|', ('specialty_ids', '=', False), ('specialty_ids', '=', user_specialty)]",
    )

    @api.constrains("service_ids")
    def _check_service_ids(self):
        for rec in self:
            if not rec.service_ids:
                raise UserError(_("Please specify at least on service"))
            rec.name = ", ".join(rec.service_ids.mapped("name"))
