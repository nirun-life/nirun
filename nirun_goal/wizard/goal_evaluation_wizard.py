#  Copyright (c) 2022 Piruin P.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GoalEvaluationWizard(models.TransientModel):
    _name = "ni.goal.evaluation.wizard"
    _description = "Goal Evaluation"

    goal_id = fields.Many2one("ni.goal", required=True)
    encounter_id = fields.Many2one(related="goal_id.encounter_id")
    goal_achievement_id = fields.Many2one(related="goal_id.achievement_id")
    goal_achievement_note = fields.Text(related="goal_id.achievement_note")
    goal_achievement_date = fields.Datetime(related="goal_id.achievement_date")
    goal_achievement_uid = fields.Many2one(related="goal_id.achievement_uid")

    achievement_id = fields.Many2one(
        "ni.goal.achievement", required=True, domain=[("goal_state", "=", "completed")]
    )
    achievement_note = fields.Text("Note")
    achievement_date = fields.Datetime(
        "Evaluate at", required=True, default=fields.Datetime.now()
    )

    def action_evaluation_save(self):
        vals = {
            "achievement_id": self.achievement_id.id,
            "achievement_note": self.achievement_note,
            "achievement_date": self.achievement_date,
            "achievement_uid": self.env.uid,
            "state": self.achievement_id.goal_state,
        }
        self.goal_id.write(vals)

    @api.constrains("achievement_date", "encounter_id")
    def check_achievement_date(self):
        if self.achievement_date.date() < self.encounter_id.period_start:
            raise ValidationError(
                _(
                    "Evaluate date must not occur before encounter start ({})".format(
                        self.encounter_id.period_start
                    )
                )
            )
