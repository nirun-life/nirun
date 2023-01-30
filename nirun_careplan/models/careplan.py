#  Copyright (c) 2021-2023. NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CarePlan(models.Model):
    _name = "ni.careplan"
    _description = "Careplan"
    _inherit = [
        "period.mixin",
        "mail.thread",
        "ir.sequence.mixin",
        "ni.workflow.request.mixin",
    ]
    _order = "identifier desc"
    _check_company_auto = True
    _check_period_start = True
    _sequence_field = "identifier"
    _workflow_occurrence = "period_start"

    name = fields.Char()
    identifier = fields.Char(default="New")
    template_id = fields.Many2one("ni.careplan.template")
    patient_id = fields.Many2one(readonly=True, states={"draft": [("readonly", False)]})
    encounter_id = fields.Many2one(
        readonly=True, states={"draft": [("readonly", False)]}
    )

    def _get_default_sequence(self):
        last_sequence = self.env[self._name].search([], order="sequence desc", limit=1)
        return last_sequence.sequence + 1 if last_sequence else 0

    sequence = fields.Integer(
        "Sequence",
        help="Determine the display order",
        index=True,
        copy=False,
        default=lambda self: self._get_default_sequence(),
    )
    description = fields.Text(copy=True, help="Summary of nature of plan")
    category_ids = fields.Many2many(
        "ni.careplan.category",
        "ni_careplan_category_rel",
        "careplan_id",
        "category_id",
        copy=True,
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
        "ni.condition",
        "ni_careplan_condition_rel",
        "careplan_id",
        "condition_id",
        readonly=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
        domain="""[('patient_id', '=', patient_id),
                   ('encounter_id', '=?', encounter_id)]""",
    )
    condition_count = fields.Integer(compute="_compute_condition_count", store=True)

    goal_ids = fields.One2many(
        "ni.goal",
        "careplan_id",
        readonly=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
        domain="""[('patient_id', '=', patient_id),
                   ('encounter_id', '=?', encounter_id),
                   ('careplan_id', '=?', id)]""",
    )
    goal_count = fields.Integer(compute="_compute_goal_count")
    goal_achieved_count = fields.Integer(compute="_compute_goal_count")
    goal_achieved = fields.Float("Achieved (%)", compute="_compute_goal_count")
    achievement_date = fields.Datetime(
        "Last Evaluation", compute="_compute_achievement_date"
    )

    activity_ids = fields.One2many(
        "ni.careplan.activity",
        "careplan_id",
        string="Activity",
        readonly=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
        domain="""[('patient_id', '=', patient_id),
                   ('encounter_id', '=?', encounter_id),
                   ('careplan_id', '=?', id)]""",
    )
    activity_count = fields.Integer(compute="_compute_activities_count", store=True)
    manager_id = fields.Many2one(
        "hr.employee",
        string="Care Manager",
        tracking=True,
        compute="_compute_manager_id",
    )
    employee_ids = fields.Many2many("hr.employee", string="Assigned to")
    create_date = fields.Datetime("Authored", readonly=True)
    create_uid = fields.Many2one("res.users", "Author", readonly=True)

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
            name = "{} : {}".format(plan.patient_id.name, name)
        return name

    @api.model
    def create(self, vals):
        plans = super(CarePlan, self).create(vals)
        plans._generate_name()
        return plans

    def _generate_name(self):
        for plan in self:
            if not plan.name:
                name = _("{} for".format(plan.intent.capitalize()))
                if plan.condition_ids:
                    problem = plan.condition_ids.mapped("name")
                    name = "{} {}".format(name, ", ".join(problem))
                else:
                    name = "{} {}".format(name, plan.patient_id.name)
                plan.name = name
        return self

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if self.template_id:
            data = self.template_id.copy_data(
                {
                    "patient_id": self.patient_id.id,
                    "encounter_id": self.encounter_id.id,
                }
            )[0]
            data["template_id"] = self.template_id.id
            if self.template_id.condition_code_ids:
                con = self.env["ni.condition.latest"].search(
                    [
                        ("patient_id", "=", self.patient_id.id),
                        ("code_id", "in", self.template_id.condition_code_ids.ids),
                    ]
                )
                data["condition_ids"] = [(4, c.id, 0) for c in con]
            self.update(data)
            self.activity_ids.copy_timing_form_template()

    @api.depends("employee_ids")
    def _compute_manager_id(self):
        for rec in self:
            rec.manager_id = rec.employee_ids[0] if len(rec.employee_ids) > 0 else None

    @api.depends("condition_count")
    def _compute_condition_count(self):
        for plan in self:
            plan.condition_count = len(plan.condition_ids)

    @api.depends("activity_ids")
    def _compute_activities_count(self):
        for plan in self:
            plan.activity_count = len(plan.activity_ids)

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

    @api.depends("goal_ids.achievement_date")
    def _compute_achievement_date(self):
        goals = self.env["ni.goal"]
        for rec in self:
            goal = goals.search(
                [
                    ("careplan_id", "=", rec.id),
                    ("state", "not in", ["proposed", "cancelled"]),
                ],
                order="achievement_date desc",
                limit=1,
            )
            rec.achievement_date = goal[0].achievement_date if goal else None

    def copy_data(self, default=None):
        if default is None:
            default = {}
        _default = dict(default)
        if "activity_ids" not in default:
            default["activity_ids"] = [
                (0, 0, act.copy_data(dict(_default))[0]) for act in self.activity_ids
            ]
        if "goal_ids" not in default:
            default["goal_ids"] = [
                (0, 0, goal.copy_data(dict(_default))[0]) for goal in self.goal_ids
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
            "nirun_goal", "goal_action"
        )
        return dict(action, context=ctx)

    def action_revoked(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Must be active state"))
        self.env["ni.careplan.activity"].search(
            [("careplan_id", "in", self.ids), ("state", "=", "in-progress")]
        ).action_cancel()
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

    def action_play(self):
        self.filtered(lambda plan: plan.state == "draft").action_confirm()
        self.filtered(lambda plan: plan.state == "on-hold").action_resume()

    def action_confirm(self):
        draft_plan = self.filtered(lambda plan: plan.state == "draft")
        draft_plan.mapped("goal_ids").action_confirm(force=True)
        draft_plan.mapped("activity_ids").action_start(force=True)
        draft_plan.write({"state": "active"})

    def action_close(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Must be active state"))
            goal = plan.goal_ids.filtered(lambda g: g.state != "completed")
            if goal:
                raise UserError(
                    _("All goals must be in completed state before close careplan")
                )
            plan.activity_ids.filtered(
                lambda a: a.state == "in-progress"
            ).action_complete()
            plan.write({"state": "completed"})
            if not plan.period_end:
                plan.period_end = fields.Date.today()

    @api.constrains("goal_ids", "encounter_id")
    def check_goal_encounter_id(self):
        # need this when create careplan in encounter page and use template
        for rec in self:
            if rec.encounter_id:
                enc = rec.goal_ids.filtered_domain(
                    [("encounter_id", "!=", rec.encounter_id.id)]
                )
                if enc:
                    enc.write({"encounter_id": rec.encounter_id.id})

    @property
    def _workflow_summary(self):
        summary = self.name or self._generate_name().name
        if self.description:
            summary = "{} - {}".format(summary, self.description)
        return summary
