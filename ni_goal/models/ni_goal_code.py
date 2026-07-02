#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class GoalCodeableConcept(models.Model):
    _name = "ni.goal.code"
    _description = "Goal Codeable Concept"
    _inherit = "ni.coding"

    category_id = fields.Many2one("ni.goal.category", index=True)
    specialty_ids = fields.Many2many(
        "hr.job",
        "ni_goal_code_specialty",
        "code_id",
        "job_id",
        help="Specialty who can assign this goal",
    )
    observation_type_id = fields.Many2one(
        "ni.observation.type",
        "Measure",
        domain=[("value_type", "in", ["int", "float", "code_id", "code_ids"])],
    )
    target_value_type = fields.Selection(related="observation_type_id.value_type")
    target_type = fields.Selection([("fix", "Fix Value"), ("ratio", "Ratio")])
    target_fix_min = fields.Float("Min")
    target_fix_max = fields.Float("Max")
    target_ratio_min = fields.Float("Ratio Min", default=1.0)
    target_ratio_max = fields.Float("Ratio Max", default=1.0)

    target_code_operator = fields.Selection(
        [
            ("=", "Match"),
            ("!=", "Not Match"),
            ("child_of", "Child of"),
            ("parent_of", "Parent of"),
            ("in", "Contain"),
            ("not in", "Not Contain"),
        ],
        "Operator",
    )
    target_code_ids = fields.Many2many(
        "ni.observation.value.code",
        "ni_goal_code_observation_value_code",
        "goal_code_id",
        "observation_value_code_id",
        domain="[('type_ids', '=', observation_type_id)]",
    )

    condition_code_ids = fields.Many2many(
        "ni.condition.code",
        "ni_condition_code_goal_code_rel",
        "goal_code_id",
        "condition_code_id",
        help="Condition addressed by this goal",
    )
