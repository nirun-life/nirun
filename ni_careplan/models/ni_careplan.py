#  Copyright (c) 2024 NSTDA

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools.date_utils import relativedelta

_logger = logging.getLogger(__name__)

LOCK_STATE_DICT = {
    "revoked": [("readonly", True)],
    "completed": [("readonly", True)],
}


class Careplan(models.Model):
    _name = "ni.careplan"
    _description = "Care Plan"
    _inherit = ["ni.workflow.request.mixin", "ni.period.mixin", "ni.identifier.mixin"]
    _check_period_start = False

    @api.model
    def default_get(self, fields):
        res = super(Careplan, self).default_get(fields)
        res["intent"] = "plan"
        return res

    period_start = fields.Datetime(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    period_end = fields.Datetime(
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda _: fields.Datetime.now() + relativedelta(months=3),
    )
    category_id = fields.Many2one(
        "ni.careplan.category",
        required=False,
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    condition_ids = fields.Many2many(
        "ni.condition",
        "ni_careplan_condition",
        "plan_id",
        "condition_id",
        domain="[('patient_id', '=', patient_id), ('clinical_state', '=', 'active')]",
        context={"default_patient_id": "patient_id"},
        states=LOCK_STATE_DICT,
    )
    condition_count = fields.Integer(compute="_compute_condition_count")
    goal_mode = fields.Selection(
        [("simple", "Simple"), ("advance", "Advance")], default="advance", required=True
    )
    goal_code_ids = fields.Many2many(
        "ni.goal.code",
        domain="['|', ('specialty_ids', '=', False), ('specialty_ids', '=', user_specialty)]",
    )
    goal_text = fields.Html()
    goal_category_id = fields.Many2one(related="category_id.goal_category_id")
    goal_ids = fields.One2many(
        "ni.goal",
        "careplan_id",
        context={"default_patient_id": "patient_id"},
        states=LOCK_STATE_DICT,
    )
    goal_review_ids = fields.One2many(related="goal_ids", string="Goal Review")
    goal_count = fields.Integer(compute="_compute_goal_ratio")
    goal_achieved_count = fields.Integer(compute="_compute_goal_ratio")
    goal_ratio = fields.Float(compute="_compute_goal_ratio")

    action_count = fields.Integer(compute="_compute_action_count")
    action_display = fields.Selection(
        [
            ("service", "Service"),
            ("medication", "Medication"),
        ],
        default="service",
    )
    service_category_id = fields.Many2one(related="category_id.service_category_id")
    service_request_ids = fields.One2many(
        "ni.service.request",
        "careplan_id",
        domain="[('category_id', '=?', service_category_id), ('intent', '=', 'plan')]",
        options="{'create': true}",
        states=LOCK_STATE_DICT,
    )
    service_request_count = fields.Integer(compute="_compute_action_count")
    medication_request_ids = fields.One2many(
        "ni.medication.request", "careplan_id", states=LOCK_STATE_DICT
    )
    medication_request_count = fields.Integer(compute="_compute_action_count")
    document_ids = fields.One2many(
        "ni.document.ref", "careplan_id", states=LOCK_STATE_DICT
    )
    document_count = fields.Integer(compute="_compute_document_count")
    achievement_id = fields.Many2one(
        "ni.goal.achievement", domain=[("careplan", "=", True)], states=LOCK_STATE_DICT
    )
    achievement_decoration = fields.Selection(related="achievement_id.decoration")
    achievement_reason = fields.Html(help="Reason for current achievement")
    achievement_date = fields.Datetime(
        help="When achievement status took effect", readonly=1
    )
    achievement_uid = fields.Many2one("res.users", readonly=1)

    def _prepare_service_value(self, s):
        return s.copy_data(
            {
                "encounter_id": self.encounter_id.id,
                "patient_id": self.patient_id.id,
                "careplan_id": self.id,
                "period_start": self.period_start,
                "period_end": self.period_end,
            }
        )[0]

    def _prepare_goal_value(self, g, condition_ids):
        self.ensure_one()
        condition = None
        if condition_ids:
            condition = condition_ids.filtered_domain(
                [("code_id", "child_of", g.condition_code_ids.ids)]
            )
        val = {
            "code_id": g.id,
            "name": g.name,
            "category_id": g.category_id.id,
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "careplan_id": self.id,
            "state_id": self.env.ref("ni_goal.goal_state_active").id,
            "condition_ids": [fields.Command.set(condition.ids)]
            if condition_ids
            else [],
        }
        return val

    @api.depends("condition_ids")
    def _compute_condition_count(self):
        for rec in self:
            rec.condition_count = len(rec.condition_ids)

    @api.depends("service_request_ids", "medication_request_ids")
    def _compute_action_count(self):
        for rec in self:
            rec.service_request_count = len(rec.service_request_ids)
            rec.medication_request_count = len(rec.medication_request_ids)
            rec.action_count = sum(
                [rec.service_request_count, rec.medication_request_count]
            )

    @api.depends("goal_ids")
    def _compute_goal_ratio(self):
        for rec in self:
            rec.goal_count = len(rec.goal_ids)
            rec.goal_achieved_count = len(
                rec.goal_ids.filtered_domain(
                    [
                        (
                            "achievement_id",
                            "child_of",
                            self.env.ref("ni_goal.goal_achieved").id,
                        )
                    ]
                )
            )
            rec.goal_ratio = (
                rec.goal_achieved_count / rec.goal_count * 100
                if rec.goal_count
                else 0.0
            )

    def write(self, vals):
        if "achievement_id" in vals:
            vals["achievement_date"] = fields.Datetime.now()
            vals["achievement_uid"] = self.env.user.id
            vals["state"] = "completed"
        return super(Careplan, self).write(vals)

    @api.depends("document_ids")
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)

    @api.constrains("service_request_ids")
    def _check_service_request(self):
        for rec in self:
            sr = rec.service_request_ids.filtered(
                lambda r: r.intent == "plan" and not r.careplan_id
            )
            if sr:
                sr.write({"careplan_id": rec.id})

    @api.constrains("goal_mode", "goal_code_ids")
    def _check_goal_text(self):
        default_state = self.env["ni.goal.state"].search([], limit=1)
        for rec in self:
            if rec.goal_mode == "simple":
                org_goal = rec.goal_ids.mapped("code_id")
                cmd = []
                for g in rec.goal_code_ids.filtered(lambda g: g not in org_goal):
                    cmd.append(
                        Command.create(
                            {
                                "patient_id": rec.patient_id.id,
                                "encounter_id": rec.encounter_id.id,
                                "name": g.name,
                                "code_id": g.id,
                                "category_id": g.category_id.id
                                if g.category_id
                                else None,
                                "state_id": default_state.id,
                            }
                        )
                    )
                for g in rec.goal_ids.filtered(
                    lambda g: g.code_id not in rec.goal_code_ids
                ):
                    cmd.append(Command.unlink(g.id))
                rec.goal_ids = cmd

    template_id = fields.Many2one(
        "ni.careplan.template",
        index=True,
        ondelete="set null",
        domain="[('category_id', '=?', category_id)]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if self.template_id and self.category_id != self.template_id.category_id:
            self.category_id = self.template_id.category_id

    def apply_template(self):
        self.ensure_one()
        if not self.template_id:
            if not self.category_id or not self.category_id.template_ids:
                raise UserError(_("Please select template"))
            else:
                first = True
                for template in self.category_id.template_ids.filtered_domain(
                    [
                        (
                            "condition_code_ids",
                            "parent_of",
                            self.patient_id.condition_code_ids.ids,
                        )
                    ]
                ):
                    self.template_id = template
                    self.with_context({"keep_careplan": not first}).apply_template()
                    first = False
                if not first:
                    self.template_id = False
                    return

        keep = self.env.context.get("keep_careplan", 0)
        logging.debug(
            f"Apply careplan template(id={self.template_id.id}) with context ('keep_careplan'={keep}) "
        )

        if self.template_id.condition_code_ids:
            condition = self.env["ni.condition"].search(
                [
                    ("patient_id", "=", self.patient_id.id),
                    ("code_id", "in", self.template_id.condition_code_ids.ids),
                    ("clinical_state", "=", "active"),
                ]
            )
            if not condition:
                condition = "\n\t".join(
                    "[{}] {}".format(c.code, c.name) if c.code else c.name
                    for c in self.template_id.mapped("condition_code_ids")
                )
                raise UserError(
                    _(
                        "Not finding patient's conditions related to selected template, "
                        "Patient should have a least one of following conditions\n\n\t{}"
                    ).format(condition)
                )
            if not keep:
                val = {"condition_ids": [fields.Command.set(condition.ids)]}
            else:
                val = {"condition_ids": [fields.Command.link(c.id) for c in condition]}
            goal = self.template_id.goal_code_ids.filtered_domain(
                [
                    "|",
                    ("condition_code_ids", "=", False),
                    (
                        "condition_code_ids",
                        "child_of",
                        condition.mapped("code_id").ids,
                    ),
                ]
            )
            if goal:
                goal_vals = [
                    fields.Command.create(self._prepare_goal_value(g, condition))
                    for g in goal
                ]
                val.update(
                    {
                        "goal_ids": [(fields.Command.clear())] + goal_vals
                        if not keep
                        else goal_vals
                    }
                )

            if self.template_id.service_request_ids:
                sr_vals = [
                    fields.Command.create(self._prepare_service_value(s))
                    for s in self.template_id.service_request_ids
                ]
                val.update(
                    {
                        "service_request_ids": [(fields.Command.clear())] + sr_vals
                        if not keep
                        else sr_vals
                    }
                )
            self.write(val)
            if self.goal_ids:
                self.goal_ids._onchange_code_id()
        else:
            raise UserError(
                _(
                    "the Selected template not properly setting the patient's conditions."
                )
            )

    def __check_period_start(self, encounter_id, period_start):
        # careplan may be created in advance or reversed way
        # so Ignore careplan.period_start and encounter.period_start check
        return

    def action_edit(self):
        self.ensure_one()
        context = dict(self.env.context)
        view = {
            "name": self[self._rec_name] or self._description,
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "target": context.pop("target", "new"),
            "res_id": self.id,
            "view_type": "form",
            "views": [[False, "form"]],
            "context": context,
        }
        return view
