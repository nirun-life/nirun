#  Copyright (c) 2024 NSTDA

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
            ("company_id", "=", False),
            ("company_id", "=", self.company_id.id or self.env.company.id),
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
    attendance_ids = fields.One2many("ni.encounter.service.attendance", "request_id")
    event_count = fields.Integer(compute="_compute_event_count")
    note = fields.Text()

    @api.depends("attendance_ids.service_event_id")
    def _compute_event_count(self):
        for rec in self:
            rec.event_count = len(
                rec.attendance_ids.mapped("service_event_id").filtered("id")
            )

    def action_view_events(self):
        self.ensure_one()
        event_ids = self.attendance_ids.mapped("service_event_id").filtered("id").ids
        return {
            "type": "ir.actions.act_window",
            "name": _("Service Events"),
            "res_model": "ni.service.event",
            "view_mode": "tree,calendar,form",
            "domain": [("id", "in", event_ids)],
        }

    def name_get(self):
        return [(rec.id, rec._get_name()) for rec in self]

    def _get_name(self):
        self.ensure_one()
        name = self.name or self.identifier or ""
        if self._context.get("show_identifier") and self.identifier:
            name = f"[{self.identifier}] {name}"
        if self._context.get("show_period") and self.period_start_date:
            end = self.period_end_date or _("ongoing")
            name = f"{name} ({self.period_start_date} → {end})"
        if self._context.get("show_state"):
            selection = dict(self._fields["state"]._description_selection(self.env))
            name = f"{name} [{selection.get(self.state, self.state)}]"
        return name

    def _default_service_domain(self):
        return [
            ("category_ids", "not in", [self.env.ref("ni_service.categ_routine").id]),
            "|",
            ("specialty_ids", "=", False),
            ("specialty_ids", "=", self.user_specialty.id),
        ]

    @api.onchange("category_id")
    def _onchange_category_id(self):
        if self.category_id:
            category_ids = (
                self.env["ni.service.category"]
                .search([("id", "child_of", self.category_id.id)])
                .ids
            )
            domain = [
                ("category_ids", "in", category_ids),
                "|",
                ("specialty_ids", "=", False),
                ("specialty_ids", "=", self.user_specialty.id),
            ]
        else:
            domain = self._default_service_domain()
        return {"domain": {"service_ids": domain}}

    @api.onchange("service_ids")
    def _onchange_service_ids(self):
        for rec in self:
            if rec.service_ids:
                name = ", ".join(rec.service_ids.mapped("name"))
                rec.name = name if len(name) <= 128 else name[:125] + "..."

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
                first_two = rec.service_ids[:2].mapped("name")
                name = ", ".join(first_two)
                name = name if len(name) <= 128 else name[:125] + "..."
                rec.name = name + f" (+{rec.service_count - 2})"
            if not rec.service_ids and not rec.name:
                raise UserError(_("Must specify at least one service"))
