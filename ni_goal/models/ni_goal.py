#  Copyright (c) 2024 NSTDA
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class Goal(models.Model):
    _name = "ni.goal"
    _description = "Goal"
    _inherit = [
        "ni.patient.res",
        "ni.period.mixin",
        "mail.thread",
        "mail.activity.mixin",
    ]

    name = fields.Char(
        "Goal Name", required=True, help="Text describing goal", tracking=True
    )
    code_id = fields.Many2one(
        "ni.goal.code",
        "Goal Code",
        index=True,
        ondelete="restrict",
        help="Code describing goal",
        domain="['|', ('specialty_ids', '=', False), ('specialty_ids', '=', user_specialty)]",
    )
    category_id = fields.Many2one("ni.goal.category")
    category_name = fields.Char("Category Name", related="category_id.name")

    achievement_id = fields.Many2one(
        "ni.goal.achievement",
        index=True,
        ondelete="restrict",
        required=False,
        domain="[('id', 'child_of', state_achievement_ids)]",
        tracking=True,
    )
    achievement_code = fields.Char(related="achievement_id.code", store=True)
    achievement_icon = fields.Char(related="achievement_id.icon")
    achievement_decoration = fields.Selection(related="achievement_id.decoration")
    achievement_color = fields.Integer(related="achievement_id.color")
    is_achieved = fields.Boolean(
        default=False, compute="_compute_is_achieved", search="_search_is_achieved"
    )

    state_id = fields.Many2one(
        "ni.goal.state",
        index=True,
        ondelete="restrict",
        required=True,
        tracking=True,
        group_expand="_expand_state_ids",
    )
    state_achievable = fields.Boolean(related="state_id.achievable")
    state_achievement_ids = fields.Many2many(related="state_id.achievement_ids")
    state_decoration = fields.Selection(related="state_id.decoration")
    state_icon = fields.Char(related="state_id.icon")
    last_comment = fields.Html(compute="_compute_last_comment")
    last_comment_author_id = fields.Many2one(
        "res.partner", compute="_compute_last_comment"
    )
    last_comment_date = fields.Datetime(compute="_compute_last_comment")

    observation_type_id = fields.Many2one(
        "ni.observation.type",
        "Measure",
        domain=[("value_type", "in", ["int", "float", "code_id", "code_ids"])],
    )
    target_value_type = fields.Selection(related="observation_type_id.value_type")
    target_min = fields.Float(default=0.0)
    target_max = fields.Float(default=100.0)
    target_code_ids = fields.Many2many(
        "ni.observation.value.code", domain="[('type_ids', '=', observation_type_id)]"
    )
    observation_id = fields.Many2one(
        "ni.observation", "Latest", compute="_compute_observation"
    )
    observation_ids = fields.Many2many("ni.observation", compute="_compute_observation")
    address_observation_id = fields.Many2one(
        "ni.observation",
        "Baseline",
        store=True,
        tracking=True,
        ondelete="set null",
    )
    outcome_observation_id = fields.Many2one(
        "ni.observation",
        "Outcome",
        store=True,
        tracking=True,
        ondelete="set null",
    )
    condition_ids = fields.Many2many(
        "ni.condition",
        "ni_goal_addresses_condition",
        "goal_id",
        "condition_id",
        domain="[('patient_id', '=', patient_id), ('clinical_state', '=', 'active')]",
    )

    @api.onchange("observation_type_id")
    def _onchange_observation_type_id(self):
        for rec in self:
            rec.update(
                {
                    "target_min": rec.observation_type_id.min,
                    "target_max": rec.observation_type_id.max,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records.filtered("observation_id"):
            rec.address_observation_id = rec.observation_id
        return records

    def write(self, vals):
        res = super().write(vals)
        if {"state_id", "achievement_id"} & vals.keys():
            for rec in self.filtered("observation_id"):
                updates = {}
                if "state_id" in vals:
                    new_state = self.env["ni.goal.state"].browse(vals["state_id"])
                    if new_state.code == "active" and not rec.address_observation_id:
                        updates["address_observation_id"] = rec.observation_id.id
                if rec.outcome_observation_id != rec.observation_id:
                    updates["outcome_observation_id"] = rec.observation_id.id
                if updates:
                    rec.write(updates)
        return res

    @api.depends("observation_type_id")
    def _compute_observation(self):
        no_ob = self.filtered_domain([("observation_type_id", "=", False)])
        if no_ob:
            no_ob.update({"observation_id": False, "observation_ids": False})
            _logger.info("Setted not ob")
        ob = self - no_ob
        if not ob:
            _logger.info("Not found ob")
            return
        for rec in ob:
            obs = self.env["ni.observation"].search(
                [
                    ("patient_id", "=", rec.patient_id.id),
                    ("type_id", "=", rec.observation_type_id.id),
                ],
                order="occurrence desc",
            )
            _logger.info("Query")
            if not obs:
                rec.update({"observation_id": False, "observation_ids": False})
            else:
                _logger.debug("Updated ob")
                rec.update(
                    {
                        "observation_id": obs[0].id,
                        "observation_ids": [fields.Command.set(obs.ids)],
                    }
                )

    @api.model
    def _expand_state_ids(self, states, domain, order):
        return states.search([], order=order)

    @api.depends("achievement_id")
    def _compute_is_achieved(self):
        achieved = self.filtered_domain(
            [("achievement_id", "child_of", self.env.ref("ni_goal.goal_achieved").id)]
        )
        if achieved:
            achieved.is_achieved = True
        not_achieved = self - achieved
        if not_achieved:
            not_achieved.is_achieved = False

    @api.depends("message_ids")
    def _compute_last_comment(self):
        for rec in self:
            msg = self.env["mail.message"].search(
                [
                    ("res_id", "=", rec.id),
                    ("model", "=", self._name),
                    ("body", "!=", False),
                    ("subtype_id", "=", self.env.ref("mail.mt_comment").id),
                ],
                order="id desc",
                limit=1,
            )
            rec.last_comment = msg.body if msg else False
            rec.last_comment_author_id = msg.author_id if msg else False
            rec.last_comment_date = msg.date if msg else False

    def _search_is_achieved(self, operator, value):
        achieved_id = self.env.ref("ni_goal.goal_achieved").id
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("achievement_id", "child_of", achieved_id)]
        achieved_ids = (
            self.env["ni.goal.achievement"]
            .search([("id", "child_of", achieved_id)])
            .ids
        )
        return [("achievement_id", "not in", achieved_ids)]

    @api.onchange("code_id")
    def _onchange_code_id(self):
        for rec in self.filtered(lambda c: c.code_id):
            code_id = rec.code_id
            rec.name = code_id.name
            rec.category_id = code_id.category_id
            rec.observation_type_id = code_id.observation_type_id
            if rec.observation_type_id:
                if code_id.target_type == "fix":
                    _logger.debug("Apply Fixed value min-max target ")
                    rec.target_min = code_id.target_fix_min
                    rec.target_max = code_id.target_fix_max
                elif code_id.target_type == "ratio":
                    _logger.debug("Apply Ratio value min-max target ")
                    last_value = float(rec.observation_id.value)
                    rec.target_min = last_value * code_id.target_ratio_min
                    rec.target_max = last_value * code_id.target_ratio_max
            rec._mapping_condition()

    def _mapping_condition(self):
        for rec in self:
            if rec.patient_id and rec.code_id and rec.code_id.condition_code_ids:
                cond = self.env["ni.condition"].search(
                    [
                        ("patient_id", "=", rec.patient_id.ids[0]),
                        ("code_id", "in", rec.code_id.condition_code_ids.ids),
                        ("clinical_state", "in", ["active"]),
                    ]
                )
                rec.condition_ids = cond

    @api.onchange("state_id")
    def _onchange_state_id(self):
        for rec in self:
            if rec.achievement_id not in rec.state_achievement_ids:
                rec.achievement_id = rec.state_id.achievement_id or None

    @api.constrains("state_id")
    def _check_state_achievement(self):
        for rec in self:
            if (
                not rec.achievement_id
                or rec.achievement_id not in rec.state_achievement_ids
            ):
                rec.achievement_id = (
                    rec.state_id.achievement_id or rec.state_achievement_ids[0]
                    if rec.state_achievement_ids
                    else None
                )

    def _open_state_wizard(self, default_state, default_achievement):
        self.ensure_one()
        return {
            "name": _("Update Goal"),
            "res_model": "ni.goal.state.wizard",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_goal_id": self.id,
                "default_state_id": self.env.ref(default_state).id,
                "default_achievement_id": self.env.ref(default_achievement).id,
            },
        }

    def action_mark_achieved(self):
        return self._open_state_wizard(
            "ni_goal.goal_state_completed", "ni_goal.goal_achieved"
        )

    def action_mark_not_achieved(self):
        return self._open_state_wizard(
            "ni_goal.goal_state_completed", "ni_goal.goal_not_achieved"
        )

    def action_state_wizard(self):
        self.ensure_one()
        return {
            "name": _("Update Goal"),
            "res_model": "ni.goal.state.wizard",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "target": "new",
            "context": {"default_goal_id": self.id},
        }

    def action_edit(self):
        self.ensure_one()
        view = {
            "name": _("Edit"),
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "res_id": self.id,
            "view_mode": "form",
            "context": self.env.context,
        }
        return view
