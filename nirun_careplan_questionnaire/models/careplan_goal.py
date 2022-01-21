#  Copyright (c) 2022 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CareplanGoal(models.Model):
    _inherit = "ni.careplan.goal"

    target_survey_id = fields.Many2one(
        "survey.survey",
        "Target Questionnaire",
        domain=[("state", "=", "open"), ("scoring_type", "!=", "no_scoring")],
    )
    target_survey_grade_id = fields.Many2one("survey.grade", "Target Grade")
    target_survey_score = fields.Float(
        "Target Score(%)", related="target_survey_grade_id.low", store=True
    )
    target_survey_response_id = fields.Many2one(
        "survey.user_input", "Result", copy=False
    )
    target_survey_response_grade_id = fields.Many2one(
        "survey.grade",
        "Result Grade",
        related="target_survey_response_id.quizz_grade_id",
    )
    target_survey_response_score = fields.Float(
        "Result Score(%)", related="target_survey_response_id.quizz_score"
    )
    target_survey_achieved = fields.Boolean(
        "Result Achieved",
        compute="_compute_target_survey_achieved",
        store=True,
        default=False,
    )
    target_survey_achieved_status_id = fields.Many2one(
        "ni.goal.achievement",
        "Status on Achieved",
        domain=[("goal_achieved", "=", True)],
    )

    @api.depends("target_survey_response_id")
    def _compute_target_survey_achieved(self):
        for rec in self:
            if rec.target_survey_response_id:
                rec.target_survey_achieved = (
                    rec.target_survey_response_score > rec.target_survey_score
                )
            else:
                rec.target_survey_achieved = False

    @api.constrains("target_survey_id")
    def _check_survey_id(self):
        for rec in self:
            if rec.target_survey_id and not rec.target_survey_id.grade_ids:
                raise ValidationError(
                    _("Only grading specified survey can be set as goal's target")
                )
            if rec.target_survey_id and not rec.target_survey_grade_id:
                raise ValidationError(
                    _("Must specify target survey's grade for goal [%s]") % rec.name
                )
            if rec.target_survey_id and not rec.target_survey_achieved_status_id:
                raise ValidationError(
                    _("Must specify achievement status for goal [%s]") % rec.name
                )

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.target_survey_response_id:
            response = self.target_survey_id._create_answer(
                partner=self.patient_id.partner_id.id,
                subject_model="ni.patient",
                subject_id=self.patient_id.id,
            )
            self.target_survey_response_id = response.id
        else:
            response = self.target_survey_response_id
        # grab the token of the response and start surveying
        action = self.target_survey_id.with_context(
            survey_token=response.token
        ).action_start_survey()
        action.update({"target": "new"})
        return action
