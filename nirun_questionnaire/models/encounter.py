#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class EncounterClassification(models.Model):
    _inherit = "ni.encounter.cls"

    survey_id = fields.Many2one(
        "survey.survey",
        "Questionnaire",
        help="Questionnaire relate for this class of encounter",
    )


class Encounter(models.Model):
    _inherit = "ni.encounter"

    survey_id = fields.Many2one(related="class_id.survey_id")
    response_id = fields.Many2one("survey.user_input", store=True)

    def action_survey_user_input_completed(self):
        action_rec = self.env.ref("survey.action_survey_user_input")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_encounter_id": self.ids[0],
                "search_default_completed": 1,
                "search_default_not_test": 1,
                "search_default_group_by_survey": 1,
            }
        )
        action["context"] = ctx
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
        """ If response is available then print this response otherwise print
        survey form (print template of the survey) """
        self.ensure_one()
        if not self.response_id:
            return self.survey_id.action_print_survey()
        else:
            action = self.survey_id.with_context(
                survey_token=self.response_id.token
            ).action_print_survey()
            action.update({"target": "new"})
            return action
