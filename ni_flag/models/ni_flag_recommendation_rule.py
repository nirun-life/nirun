#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class FlagRecommendationRule(models.Model):
    _name = "ni.flag.recommendation.rule"
    _description = "Flag Recommendation Rule"
    _order = "sequence, name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    observation_type_id = fields.Many2one(
        "ni.observation.type", required=True, ondelete="cascade", index=True
    )
    interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        ondelete="restrict",
        help="Match when the observation has this interpretation.",
    )
    value_code_id = fields.Many2one(
        "ni.observation.value.code",
        ondelete="restrict",
        help="Match when a single-choice observation has this value code.",
    )
    value_code_ids = fields.Many2many(
        "ni.observation.value.code",
        "ni_flag_rule_value_code_rel",
        "rule_id",
        "value_code_id",
        help="Match when a multi-choice observation includes any of these values.",
    )
    flag_code_id = fields.Many2one("ni.flag.code", required=True, ondelete="restrict")
    scope = fields.Selection(
        [("patient", "Patient"), ("encounter", "Encounter")],
        required=True,
        default="encounter",
    )
    mode = fields.Selection(
        [("recommend", "Recommend"), ("auto_apply", "Auto Apply")],
        required=True,
        default="recommend",
    )
    note = fields.Text()

    def _matches_observation(self, observation):
        self.ensure_one()
        if not self.active or observation.type_id != self.observation_type_id:
            return False
        if (
            self.interpretation_id
            and observation.interpretation_id != self.interpretation_id
        ):
            return False
        if self.value_code_id and observation.value_code_id != self.value_code_id:
            return False
        if self.value_code_ids and not (
            observation.value_code_ids & self.value_code_ids
        ):
            return False
        return True

    def _recommendation_vals(self, observation):
        encounter_id = (
            observation.encounter_id.id if self.scope == "encounter" else False
        )
        return {
            "name": self.name,
            "patient_id": observation.patient_id.id,
            "encounter_id": encounter_id,
            "flag_code_id": self.flag_code_id.id,
            "rule_id": self.id,
            "source_observation_id": observation.id,
            "reason": self.note or self.name,
        }

    def evaluate_observation(self, observation):
        Recommendation = self.env["ni.flag.recommendation"]
        for rule in self:
            if not rule._matches_observation(observation):
                continue
            recommendation = Recommendation.search(
                [
                    ("rule_id", "=", rule.id),
                    ("source_observation_id", "=", observation.id),
                ],
                limit=1,
            )
            if not recommendation:
                recommendation = Recommendation.create(
                    rule._recommendation_vals(observation)
                )
            if rule.mode == "auto_apply" and recommendation.state != "auto_applied":
                recommendation.action_auto_apply()
