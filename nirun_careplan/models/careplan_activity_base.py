#  Copyright (c) 2022 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Activity(models.AbstractModel):
    _name = "ni.careplan.activity.base"
    _description = "Careplan Activity"
    _order = "sequence"

    sequence = fields.Integer(help="Determine the display order", index=True)
    color = fields.Integer(string="Color Index")

    careplan_id = fields.Many2one(
        "ni.careplan",
        string="Care Plan",
        required=True,
        check_company=True,
        ondelete="cascade",
        copy=False,
        default=lambda self: self.env.context.get("default_careplan_id"),
    )
    company_id = fields.Many2one(
        related="careplan_id.company_id", store=True, readonly=True, index=True
    )
    code_id = fields.Many2one(
        "ni.careplan.activity.code",
        "Activity",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    name = fields.Char(string="Activity", related="code_id.name")
    display_name = fields.Char(compute="_compute_display_name")
    description = fields.Html(string="Description")
    category_id = fields.Many2one("ni.careplan.category", tracking=True)
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Important")],
        default="0",
        index=True,
        string="Priority",
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
        copy=False,
        group_expand="_group_expand_state",
    )
    _sql_constraints = [
        (
            "code__uniq",
            "unique (careplan_id, code_id)",
            "Activity must be unqiue!",
        ),
    ]

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        goal = self
        name = goal.name or goal.code_id.name
        if self._context.get("show_patient"):
            name = "{} - {}".format(goal.patient_id._name_get(), name)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, goal.get_state_label())
        return name

    def get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    @api.model
    def _group_expand_state(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            if rec.category_id and not rec.color:
                rec.color = rec.category_id.color

    @api.depends("name")
    def _compute_display_name(self):
        diff = dict(show_patient=None, show_state=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    def action_start(self, force=False):
        if not force:
            for act in self:
                if act.state != "scheduled":
                    raise ValidationError(_("Must be scheduled state"))
        self.write({"state": "in-progress"})

    def action_complete(self):
        for act in self:
            if act.state == "cancelled":
                raise ValidationError(_("Must be not be cancelled"))
        self.write({"state": "completed"})

    def action_cancel(self):
        for act in self:
            if act.state == "completed":
                raise ValidationError(_("Must be not be completed"))
        self.write({"state": "cancelled"})
