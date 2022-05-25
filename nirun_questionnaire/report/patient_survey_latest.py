#  Copyright (c) 2022 Piruin P.

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError


class PatientSurveyLatest(models.Model):
    _name = "ni.patient.survey_latest"
    _description = "Patient's latest survey result"
    _auto = False

    company_id = fields.Many2one("res.company", readonly=True)
    survey_id = fields.Many2one("survey.survey", readonly=True)
    patient_id = fields.Many2one("ni.patient", readonly=True)
    deceased = fields.Boolean(related="patient_id.deceased")
    gender = fields.Selection(related="patient_id.gender")
    encounter_id = fields.Many2one("ni.encounter", readonly=True)
    encounter_state = fields.Selection(related="encounter_id.state")
    quizz_grade_id = fields.Many2one(
        "survey.grade", "Grade", readonly=True, compute=False
    )
    quizz_grade = fields.Char("Grade", related="quizz_grade_id.name")
    quizz_score = fields.Float(
        "Score (%)", readonly=True, compute=False, group_operator="avg"
    )
    quizz_score_raw = fields.Float(
        "Score", readonly=True, compute=False, group_operator="avg"
    )
    quizz_score_total = fields.Float(
        "Total Score", readonly=True, compute=False, group_operator="avg"
    )
    create_date = fields.Datetime("Authored", readonly=True)
    create_uid = fields.Many2one("res.users", "Author")
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
                WHERE state = 'done'
                GROUP BY patient_id, survey_id
            )
        )
        """
            % (self._table)
        )

    def action_survey_subject_wizard(self):
        self.ensure_one()
        return self._get_survey_user_input().action_survey_subject_wizard()

    def action_graph_view(self):
        self.ensure_one()
        return self._get_survey_user_input().action_graph_view()

    def action_print_answers(self):
        self.ensure_one()
        return self._get_survey_user_input().action_print_answers()

    def _get_survey_user_input(self):
        response_id = self.env["survey.user_input"].browse(self.id)
        if not response_id:
            raise ValidationError(_("Not found requested survey's response!"))
        return response_id
