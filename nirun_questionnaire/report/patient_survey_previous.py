#  Copyright (c) 2022 Piruin P.

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError


class PatientSurveyPrevious(models.Model):
    _name = "ni.patient.survey_previous"
    _description = "Patient's previous survey result"
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
            f"""CREATE OR REPLACE VIEW {self._table} AS
        WITH ranked_survey_input AS (
            SELECT
                ROW_NUMBER() OVER
                (PARTITION BY patient_id,survey_id ORDER BY id DESC) AS rn,
                *
            FROM survey_user_input
        )
        SELECT *
        FROM ranked_survey_input
        WHERE rn = 2
        """
        )

    def name_get(self):
        return [(survey_input.id, survey_input._get_name()) for survey_input in self]

    def _get_name(self):
        survey_input = self
        name = "%s" % survey_input.create_date.strftime("%Y-%m-%d %H:%M:%S")
        if survey_input.quizz_grade_id:
            name = "{} ({}%)\n{}".format(
                survey_input.quizz_grade_id.display_name,
                survey_input.quizz_score,
                name,
            )
        elif survey_input.survey_id.scoring_type != "no_scoring":
            name = "{}%\n{}".format(survey_input.quizz_score, name)
        if self.env.context.get("show_survey"):
            name = "{}: {}".format(survey_input.survey_id.display_name, name)

        return name

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
