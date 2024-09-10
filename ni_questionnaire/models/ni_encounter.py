#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    survey_id = fields.Many2one(related="class_id.survey_id")
    response_id = fields.Many2one(
        "survey.user_input", store=True, groups="survey.group_survey_user"
    )
    response_latest_ids = fields.One2many(
        "ni.encounter.survey_latest", "encounter_id", "Latest Surveys"
    )
    response_latest_id = fields.Many2one(
        "ni.encounter.survey_latest",
        "Latest Survey",
        compute="_compute_response",
        store=True,
        compute_sudo=True,
    )
    response_latest_grade_id = fields.Many2one(
        "survey.grade",
        "Latest Survey Grade",
        compute="_compute_response",
        store=True,
        compute_sudo=True,
        index=True,
    )
    response_latest_date = fields.Datetime(
        "Latest Survey Date", compute="_compute_response", store=True, compute_sudo=True
    )

    @api.depends("response_ids", "response_latest_ids")
    def _compute_response(self):
        w_survey = self.filtered_domain([("survey_id", "!=", False)])
        for rec in w_survey:
            survey_id = rec.class_id.survey_id
            latest = rec.response_latest_ids.filtered_domain(
                [("survey_id", "=", survey_id.id)]
            )

            rec.write(
                {
                    "response_latest_id": latest.id or None,
                    "response_latest_grade_id": latest.grade_id.id or None,
                    "response_latest_date": latest.create_date or None,
                }
            )
        wo_survey = self - w_survey
        wo_survey.write(
            {
                "response_latest_id": None,
                "response_latest_grade_id": None,
                "response_latest_date": None,
            }
        )

    def action_survey_user_input_completed(self):
        action = self.patient_id.action_survey_user_input_completed()
        if self.state in ["draft", "planned", "in-progress"]:
            action["context"].update(
                {
                    "default_subject_ni_encounter": self.id,
                }
            )
        return action

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.survey_id._create_answer(
                partner=self.partner_id,
                subject_model="ni.encounter",
                subject_id=self.id,
            )
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        action = self.survey_id.with_context(
            survey_token=response.token
        ).action_start_survey()
        action.update({"target": "new"})
        return action

    def action_print_survey(self):
        """If response is available then print this response otherwise print
        survey form (print template of the survey)"""
        self.ensure_one()
        if not self.response_id:
            return self.survey_id.action_print_survey()
        else:
            action = self.survey_id.with_context(
                survey_token=self.response_id.token
            ).action_print_survey()
            action.update({"target": "new"})
            return action

    def action_survey_subject(self):
        action_rec = self.env.ref("survey_subject.survey_subject_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_subject_ni_encounter": self.id,
                "default_subject_ni_patient": self.patient_id.id,
            }
        )
        action["context"] = ctx
        return action
