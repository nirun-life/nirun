#  Copyright (c) 2022 Piruin P.

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError


class PatientSurveyLatest(models.Model):
    _name = "ni.patient.survey_latest"
    _auto = False

    company_id = fields.Many2one("res.company", readonly=True)
    survey_id = fields.Many2one("survey.survey", readonly=True)
    patient_id = fields.Many2one("ni.patient", readonly=True)
    gender = fields.Selection(related="patient_id.gender")
    encounter_id = fields.Many2one("ni.encounter", readonly=True)
    encounter_state = fields.Selection(related="encounter_id.state")
    quizz_grade_id = fields.Many2one("survey.grade", readonly=True, compute=False)
    quizz_grade = fields.Char(related="quizz_grade_id.name")
    quizz_score = fields.Float(readonly=True, compute=False)
    quizz_score_raw = fields.Float(readonly=True, compute=False)
    quizz_score_total = fields.Float(readonly=True, compute=False)
    create_date = fields.Datetime(readonly=True)
    partner_id = fields.Many2one("res.partner", "Author")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT *
            FROM survey_user_input
            WHERE id IN (
                SELECT max(id)
                FROM survey_user_input
                GROUP BY patient_id, survey_id
            )
        )
        """
            % (self._table)
        )

    def action_survey_subject_wizard(self):
        self.ensure_one()
        res = self.survey_id.action_survey_subject_wizard()
        if self.survey_id.category in ["ni_patient", "ni_encounter"]:
            res["context"].update(
                {
                    "default_subject_ni_patient": self.patient_id.id,
                    "default_subject_ni_encounter": self.patient_id.encounter_id.id,
                }
            )
        return res

    def action_graph_view(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.survey_id.title,
            "res_model": "survey.user_input",
            "view_mode": "graph",
            "target": "current",
            "domain": [("survey_id", "=", self.survey_id.id)],
            "context": {
                "graph_view_ref": "nirun_questionnaire.survey_user_input_view_graph"
            },
            "views": [[False, "graph"]],
        }

    def action_print_survey(self):
        self.ensure_one()
        response_id = self.env["survey.user_input"].browse(self.id)
        if not response_id:
            raise ValidationError(_("Not found requested survey's response!"))
        action = self.survey_id.with_context(
            survey_token=response_id.token
        ).action_print_survey()
        action.update({"target": "new"})
        return action
