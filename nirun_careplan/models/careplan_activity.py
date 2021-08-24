#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


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
    name = fields.Char(string="Activity", tracking=True, required=True, index=True)
    description = fields.Html(string="Description")
    category_id = fields.Many2one("ni.careplan.category", tracking=True)

    sequence = fields.Integer(help="Determine the display order", index=True)
    color = fields.Integer(string="Color Index")
    careplan_id = fields.Many2one(
        "ni.careplan",
        string="Care Plan",
        required=True,
        check_company=True,
        ondelete="cascade",
        default=lambda self: self.env.context.get("default_careplan_id"),
    )
    company_id = fields.Many2one(
        related="careplan_id.company_id", store=True, readonly=True, index=True
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
        "ni.patient", related="careplan_id.patient_id", store=True
    )
    encounter_id = fields.Many2one("ni.encounter", related="careplan_id.encounter_id",)
    manager_id = fields.Many2one(
        string="Care Manager", related="careplan_id.manager_id", readonly=True,
    )
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
    assignee_uid = fields.Many2one(
        related="assignee_id.user_id", string="Assigned User", store=True
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

    # def name_get(self):
    #     if self.env.context.get("show_id"):
    #         return [(a.id, "%s #%d" % (a.name, a.id)) for a in self]
    #     return super(Activity, self).name_get()

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
        if (
            vals.get("period_start")
            and fields.Date.to_date(vals.get("period_start")) >= fields.Date.today()
        ):
            vals["state"] = "in-progress"

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

    @api.onchange("careplan_id")
    def _onchange_careplan(self):
        for rec in self:
            if rec.careplan_id:
                rec.write(
                    {
                        "period_start": rec.careplan_id.period_start,
                        "period_end": rec.careplan_id.period_end,
                    }
                )

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            if rec.category_id and not rec.color:
                rec.color = rec.category_id.color
