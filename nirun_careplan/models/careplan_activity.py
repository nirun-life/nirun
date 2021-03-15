#  Copyright (c) 2021 Piruin P.

import random

from odoo import _, api, fields, models


class Activity(models.Model):
    _name = "ni.careplan.activity"
    _description = "Activity"
    _inherit = ["mail.thread", "mail.activity.mixin", "period.mixin"]
    _order = "priority desc, sequence, id desc"
    _check_company_auto = True

    priority = fields.Selection(
        [("0", "Normal"), ("1", "Important")],
        default="0",
        index=True,
        string="Priority",
    )
    active = fields.Boolean(default=True)
    name = fields.Char(string="Title", tracking=True, required=True, index=True)
    description = fields.Html(string="Description")
    category_ids = fields.Many2many(
        "ni.careplan.category",
        "ni_careplan_activity_category_rel",
        "activity_id",
        "category_id",
        tracking=True,
    )
    sequence = fields.Integer(help="Determine the display order", index=True)
    color = fields.Integer(
        string="Color Index", default=lambda _: random.randint(0, 10)
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    careplan_id = fields.Many2one(
        "ni.careplan",
        string="Care plan",
        required=True,
        check_company=True,
        default=lambda self: self.env.context.get("default_careplan_id"),
    )
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("in-progress", "In-Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
        tracking=True,
        group_expand="_group_expand_state",
    )
    kanban_state = fields.Selection(
        [("normal", "Grey"), ("done", "Green"), ("blocked", "Red")],
        string="Kanban State",
        copy=False,
        default="normal",
        required=True,
    )

    patient_id = fields.Many2one(
        "ni.patient", related="careplan_id.patient_id", string="Patient", readonly=True,
    )
    manager_id = fields.Many2one(
        "hr.employee",
        string="Care Manager",
        related="careplan_id.manager_id",
        readonly=True,
    )
    color = fields.Integer(string="Color Index")
    attachment_ids = fields.One2many(
        "ir.attachment",
        compute="_compute_attachment_ids",
        string="Main Attachments",
        help="Attachment that don't come from message.",
    )
    assignee_id = fields.Many2one(
        "hr.employee",
        string="Assigned to",
        index=True,
        tracking=True,
        check_company=True,
    )
    reason = fields.Html(
        copy=True, help="Reason why this activity should be done!", tracking=True,
    )
    goal = fields.Html(
        copy=True, help="Expressed desired health state to be achieved", tracking=True,
    )
    create_date = fields.Datetime("Created On", readonly=True, index=True)
    write_date = fields.Datetime("Last Updated On", readonly=True, index=True)
    assign_date = fields.Datetime(copy=False, readonly=True)
    last_state_update = fields.Datetime(copy=False, readonly=True)

    def name_get(self):
        if self.env.context.get("show_id"):
            return [(a.id, "%s #%d" % (a.name, a.id)) for a in self]
        return super(Activity, self).name_get()

    def _compute_attachment_ids(self):
        for activity in self:
            attachment_ids = (
                self.env["ir.attachment"]
                .search([("res_id", "=", activity.id), ("res_model", "=", self._name)])
                .ids
            )
            message_attachment_ids = activity.mapped("message_ids.attachment_ids").ids
            activity.attachment_ids = [
                (6, 0, list(set(attachment_ids) - set(message_attachment_ids)))
            ]

    @api.model
    def _group_expand_state(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.model
    def create(self, vals):
        now = fields.Datetime.now()
        context = dict(self.env.context)
        if vals.get("careplan_id") and not context.get("default_careplan_id"):
            context["default_careplan_id"] = vals.get("careplan_id")
        if vals.get("assignee_id"):
            vals["assign_date"] = now
        if vals.get("state"):
            vals["last_state_update"] = now
        return super().create(vals)

    def write(self, vals):
        now = fields.Datetime.now()
        if vals.get("state"):
            vals["last_state_update"] = now
            if "kanban_state" not in vals:
                vals["kanban_state"] = "normal"
        if vals.get("assignee_id") and "assign_date" not in vals:
            vals["assign_date"] = now
        return super().write(vals)

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get("name"):
            default["name"] = _("%s (copy)") % self.name
        return super().copy(default)
