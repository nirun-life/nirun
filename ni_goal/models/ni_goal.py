#  Copyright (c) 2024 NSTDA
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Goal(models.Model):
    _name = "ni.goal"
    _description = "Goal"
    _inherit = ["ni.patient.res", "ni.period.mixin"]

    name = fields.Char("Goal Name", required=True, help="Text describing goal")
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
    )
    achievement_decoration = fields.Selection(related="achievement_id.decoration")
    achievement_color = fields.Integer(related="achievement_id.color")
    is_achieved = fields.Boolean(default=False, compute="_compute_is_achieved")

    state_id = fields.Many2one(
        "ni.goal.state", index=True, ondelete="restrict", required=True
    )
    state_achievable = fields.Boolean(related="state_id.achievable")
    state_achievement_ids = fields.Many2many(related="state_id.achievement_ids")
    state_decoration = fields.Selection(related="state_id.decoration")

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

    @api.onchange("code_id")
    def _onchange_code_id(self):
        for rec in self.filtered(lambda c: c.code_id):
            rec.name = rec.code_id.name
            rec.category_id = rec.code_id.category_id
            rec.observation_type_id = rec.code_id.observation_type_id
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

    def action_mark_achieved(self):
        self.write(
            {
                "state_id": self.env.ref("ni_goal.goal_state_completed"),
                "achievement_id": self.env.ref("ni_goal.goal_achieved"),
            }
        )

    def action_mark_not_achieved(self):
        self.write(
            {
                "state_id": self.env.ref("ni_goal.goal_state_completed"),
                "achievement_id": self.env.ref("ni_goal.goal_not_achieved"),
            }
        )
