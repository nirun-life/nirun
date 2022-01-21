#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CarePlan(models.Model):
    _name = "ni.careplan"
    _description = "Careplan"
    _inherit = ["period.mixin", "mail.thread", "ni.patient.res", "ir.sequence.mixin"]
    _order = "period_start DESC, id DESC"
    _check_company_auto = True
    _check_period_start = True

    name = fields.Char("Plan No.", default="New")
    patient_id = fields.Many2one(readonly=True, states={"draft": [("readonly", False)]})
    encounter_id = fields.Many2one(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    sequence = fields.Integer(
        "Sequence", help="Determine the display order", index=True, default=16
    )
    description = fields.Text(copy=True, help="Summary of nature of plan")

    patient_avatar = fields.Image(
        related="patient_id.image_512", attactment=False, store=False
    )
    category_ids = fields.Many2many(
        "ni.careplan.category",
        "ni_careplan_category_rel",
        "careplan_id",
        "category_id",
        store=True,
        readonly=False,
        compute="_compute_activity_category",
    )
    intent = fields.Selection(
        [
            ("order", "Order"),
            ("plan", "Plan"),
            ("proposal", "Proposal"),
            ("option", "Option"),
        ],
        default="plan",
        help="Indicating the degree of authority/intentionality of care plan.",
    )
    author_id = fields.Many2one(
        "res.users",
        string="Author",
        default=lambda self: self.env.user,
        tracking=True,
        copy=False,
    )
    manager_id = fields.Many2one("hr.employee", string="Care Manager", tracking=True)
    contributor_ids = fields.Many2many(
        "hr.employee",
        "ni_careplan_contributor",
        "careplan_id",
        "contributor_id",
        copy=False,
    )
    patient_contribution = fields.Boolean(
        default=False,
        help="Whether patient have contribution in this care plan",
        copy=False,
    )
    period_start = fields.Date(copy=False)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "In-Progress"),
            ("on-hold", "On-Hold"),
            ("revoked", "Revoked"),
            ("completed", "Completed"),
        ],
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        default="draft",
    )
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(
        default=True,
        help="If the active field is set to False, it will allow you to"
        " hide the care plan without removing it.",
    )
    condition_ids = fields.Many2many(
        "ni.condition", "ni_careplan_condition_rel", "careplan_id", "condition_id"
    )
    condition_count = fields.Integer(compute="_compute_condition_count", store=True)

    activity_ids = fields.One2many(
        "ni.careplan.activity",
        "careplan_id",
        string="Activity",
        readonly=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
    )
    activity_count = fields.Integer(compute="_compute_activities_count", store=True)

    goal_ids = fields.One2many(
        "ni.careplan.goal",
        "careplan_id",
        readonly=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
    )
    goal_count = fields.Integer(compute="_compute_goal_count")
    goal_achieved_count = fields.Integer(compute="_compute_goal_count")
    goal_achieved = fields.Float("Achieved (%)", compute="_compute_goal_count")

    achievement_id = fields.Many2one(
        "ni.goal.achievement",
        readonly=True,
        copy=False,
        states={"completed": [("readonly", False)]},
    )
    achievement_note = fields.Text(
        readonly=True, copy=False, states={"completed": [("readonly", False)]}
    )
    template_id = fields.Many2one("ni.careplan.template", copy=False)

    def name_get(self):
        res = []
        for plan in self:
            name = plan._get_name()
            res.append((plan.id, name))
        return res

    def _get_name(self):
        plan = self
        name = plan.name
        if self.env.context.get("show_patient"):
            name = "{} {}".format(plan.patient_id.name, name)
        return name

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if self.template_id:
            data = self.template_id.copy_data()
            self.update(data[0])
            self.activity_ids.copy_timing_form_template()
            self.template_id = False

    @api.onchange("encounter_id")
    def _onchange_encounter_id(self):
        if self.encounter_id.period_start:
            self.period_start = self.encounter_id.period_start
        if self.encounter_id.period_end:
            self.period_end = self.encounter_id.period_end

    @api.depends("condition_count")
    def _compute_condition_count(self):
        for plan in self:
            plan.condition_count = len(plan.condition_ids)

    @api.depends("activity_ids")
    def _compute_activities_count(self):
        for plan in self:
            plan.activity_count = len(plan.activity_ids)

    @api.depends("category_ids", "activity_ids.category_id")
    def _compute_activity_category(self):
        for plan in self:
            c1 = plan.mapped("activity_ids.category_id.id")
            c2 = plan.mapped("category_ids.id")
            plan.category_ids = list(set().union(c1, c2))

    @api.depends("goal_ids", "goal_ids.achievement_id")
    def _compute_goal_count(self):
        for plan in self:
            plan.goal_count = len(plan.goal_ids)
            plan.goal_achieved_count = len(plan.goal_ids.filtered(lambda g: g.achieved))
            if plan.goal_count:
                plan.goal_achieved = (
                    plan.goal_achieved_count / plan.goal_count
                ) * 100.0
            else:
                plan.goal_achieved = 0.0

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if "activity_ids" not in default:
            default["activity_ids"] = [
                (0, 0, act.copy_data()[0]) for act in self.activity_ids
            ]
        if "goal_ids" not in default:
            default["goal_ids"] = [
                (0, 0, goal.copy_data()[0]) for goal in self.goal_ids
            ]
        return super().copy_data(default)

    # -------------
    # Actions
    # -------------
    def open_activity(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx.update(
            {"search_default_careplan_id": self.id, "default_careplan_id": self.id}
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_activity_action_from_careplan"
        )
        return dict(action, context=ctx)

    def open_goal(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx.update(
            {"search_default_careplan_id": self.id, "default_careplan_id": self.id}
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_goal_action_from_careplan"
        )
        return dict(action, context=ctx)

    @api.model
    def open_sub_careplan(self):
        ctx = dict(self._context)
        ctx.update({"search_default_parent_id": self.id})
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_activity_action_from_careplan"
        )
        return dict(action, context=ctx)

    def action_revoked(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Must be active state"))
        self.write({"state": "revoked"})

    def action_hold_on(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Must be active state"))
        self.write({"state": "on-hold"})

    def action_resume(self):
        for plan in self:
            if plan.state != "on-hold":
                raise UserError(_("Must be on-hold state"))
        self.write({"state": "active"})

    def action_confirm(self):
        draft_plan = self.filtered(lambda plan: plan.state == "draft")

        draft_plan.mapped("goal_ids").action_confirm(force=True)
        draft_plan.write({"state": "active"})

    def action_close(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Must be active state"))
            active_goal = plan.goal_ids.filtered(lambda g: g.state != "completed")
            if active_goal:
                raise UserError(
                    _("All goals must be in completed state before close careplan")
                )

            plan.update({"state": "completed"})
            if not plan.period_end:
                plan.period_end = fields.Date.today()
