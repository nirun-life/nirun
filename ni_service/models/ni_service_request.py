#  Copyright (c) 2024 NSTDA
import pprint

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ServiceRequest(models.Model):
    _name = "ni.service.request"
    _description = "Service Request"
    _inherit = [
        "ni.workflow.request.mixin",
        "ni.timing.mixin",
        "ni.identifier.mixin",
        "ni.period.mixin",
    ]
    _rec_name = "name"

    name = fields.Char("Service Name", required=True)
    category_id = fields.Many2one(
        "ni.service.category",
        domain=lambda self: [
            ("id", "!=", self.env.ref("ni_service.categ_routine").id),
            "|",
            ("specialty_ids", "=", False),
            ("specialty_ids", "=", self.user_specialty.id),
        ],
    )
    service_ids = fields.Many2many(
        "ni.service",
        "ni_service_request_service",
        "request_id",
        "service_id",
        check_company=True,
    )
    service_count = fields.Integer(compute="_compute_service_count")
    body_site_ids = fields.Many2many(
        "ni.body.site", "ni_service_request_body_site", "request_id", "site_id"
    )
    color = fields.Integer(compute="_compute_color")
    note = fields.Text()

    def _default_service_domain(self):
        return [
            ("category_id", "!=", self.env.ref("ni_service.categ_routine").id),
            "|",
            ("specialty_ids", "=", False),
            ("specialty_ids", "=", self.user_specialty.id),
        ]

    @api.onchange("category_id")
    def _onchange_category_id(self):
        if self.category_id:
            domain = [
                ("category_id", "=", self.category_id.id),
                "|",
                ("specialty_ids", "=", False),
                ("specialty_ids", "=", self.user_specialty.id),
            ]
        else:
            domain = self._default_service_domain()
        pprint.pprint(domain)
        return {"domain": {"service_ids": domain}}

    @api.onchange("service_ids")
    def _onchange_service_ids(self):
        for rec in self:
            if rec.service_ids:
                rec.name = ", ".join(rec.service_ids.mapped("name"))

    @api.depends("service_ids")
    def _compute_service_count(self):
        for rec in self:
            rec.service_count = len(rec.service_ids)

    @api.depends("service_ids")
    def _compute_color(self):
        for rec in self:
            rec.color = rec.service_ids[0].color if rec.service_ids else 0

    @api.constrains("name", "service_ids")
    def _check_name_service(self):
        for rec in self:
            if rec.service_ids and not rec.name:
                rec.name = ", ".join(rec.service_ids.mapped("name"))
            if not rec.service_ids and not rec.name:
                raise UserError(_("Must specify at least one service"))
