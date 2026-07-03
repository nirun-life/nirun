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
    target_type = fields.Selection(
        [("fix", "Fix Value"), ("ratio", "Ratio")],
        help="How the numeric target range (target_min/target_max) is derived when this template is applied to a "
        "goal: 'Fix Value' copies target_fix_min/target_fix_max as-is; 'Ratio' multiplies the patient's current "
        "observation value by target_ratio_min/target_ratio_max (e.g. a ratio of 0.9-1.1 targets within 90%-110% "
        "of the patient's value at the time the goal is created).",
    )
    target_fix_min = fields.Float(
        "Min", help="Fixed lower bound applied when Target Type is 'Fix Value'."
    )
    target_fix_max = fields.Float(
        "Max", help="Fixed upper bound applied when Target Type is 'Fix Value'."
    )
    target_ratio_min = fields.Float(
        "Ratio Min",
        default=1.0,
        help="Multiplier applied to the patient's current observation value to get the target lower bound when "
        "Target Type is 'Ratio'.",
    )
    target_ratio_max = fields.Float(
        "Ratio Max",
        default=1.0,
        help="Multiplier applied to the patient's current observation value to get the target upper bound when "
        "Target Type is 'Ratio'.",
    )

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
        help="How the observed value(s) must relate to the target codes: "
        "'Match'/'Not Match' compare the observed values against the target set exactly (order doesn't matter); "
        "'Contain'/'Not Contain' require every observed value to be (not be) a member of the target set; "
        "'Child of'/'Parent of' require every observed value to be a descendant/ancestor (or itself) of some target "
        "value, walking the target codes' parent hierarchy.",
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
