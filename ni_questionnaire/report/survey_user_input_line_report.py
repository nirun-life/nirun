#  Copyright (c) 2025 NSTDA
from odoo import fields, models, tools


class SurveyUserInputLineMonthlyReport(models.Model):
    _name = "survey.user_input.line.monthly.report"
    _description = "Survey User Input Line Monthly Report"
    _rec_name = "user_input_id"
    _order = "question_sequence, id"
    _auto = False

    # --- User Input ---
    user_input_id = fields.Many2one(
        "survey.user_input", string="User Input", readonly=True, index=True
    )
    survey_id = fields.Many2one("survey.survey", string="Survey", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    patient_id = fields.Many2one("ni.patient", string="Patient", readonly=True)

    # --- Question ---
    question_id = fields.Many2one(
        "survey.question", string="Question", readonly=True, index=True
    )
    page_id = fields.Many2one("survey.question", string="Page", readonly=True)
    question_sequence = fields.Integer(string="Question Sequence", readonly=True)

    # --- Answer ---
    skipped = fields.Boolean("Skipped", readonly=True)
    answer_type = fields.Selection(
        [
            ("text_box", "Free Text"),
            ("char_box", "Text"),
            ("numerical_box", "Number"),
            ("date", "Date"),
            ("datetime", "Datetime"),
            ("suggestion", "Suggestion"),
        ],
        string="Answer Type",
        readonly=True,
    )
    value_char_box = fields.Char("Text answer", readonly=True)
    value_numerical_box = fields.Float("Numerical answer", readonly=True)
    value_date = fields.Date("Date answer", readonly=True)
    value_datetime = fields.Datetime("Datetime answer", readonly=True)
    value_text_box = fields.Text("Free Text answer", readonly=True)
    suggested_answer_id = fields.Many2one(
        "survey.question.answer", string="Suggested answer", readonly=True
    )
    matrix_row_id = fields.Many2one(
        "survey.question.answer", string="Row answer", readonly=True
    )

    # --- Scoring ---
    answer_score = fields.Float("Score", readonly=True)
    answer_is_correct = fields.Boolean("Correct", readonly=True)

    # --- Dates ---
    create_date = fields.Datetime("Created on", readonly=True)

    @property
    def _table_query(self):
        return """
            SELECT
                A.id,
                A.user_input_id,
                A.question_id,
                A.skipped,
                A.answer_type,
                A.value_char_box,
                A.value_numerical_box,
                A.value_date,
                A.value_datetime,
                A.value_text_box,
                A.suggested_answer_id,
                A.matrix_row_id,
                A.answer_score,
                A.answer_is_correct,
                A.create_date,
                q.sequence           AS question_sequence,
                q.page_id            AS page_id,
                i.survey_id          AS survey_id,
                i.partner_id         AS partner_id,
                latest.patient_id    AS patient_id
            FROM survey_user_input_line A
            JOIN survey_user_input i ON i.id = A.user_input_id
            JOIN survey_question q   ON q.id = A.question_id
            JOIN (
                SELECT
                    max(id)                              AS id,
                    patient_id,
                    survey_id,
                    DATE_TRUNC('month', create_date)     AS month
                FROM survey_user_input
                WHERE state = 'done'
                GROUP BY patient_id, survey_id, DATE_TRUNC('month', create_date)
            ) latest ON
                A.user_input_id = latest.id
                AND DATE_TRUNC('month', A.create_date) = latest.month
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"CREATE OR REPLACE VIEW {self._table} AS ({self._table_query})"
        self.env.cr.execute(query)
