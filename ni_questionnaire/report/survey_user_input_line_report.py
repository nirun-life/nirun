#  Copyright (c) 2025 NSTDA
from odoo import api, fields, models, tools


class SurveyUserInputLineMonthlyReport(models.Model):
    _name = "survey.user_input.line.monthly.report"
    _inherit = "survey.user_input.line"
    _description = "Survey User Input Line Monthly Report"
    _rec_name = "user_input_id"
    _order = "question_sequence, id"
    _auto = False

    user_input_id = fields.Many2one(
        "survey.user_input", string="User Input", readonly=True, index=True
    )
    survey_id = fields.Many2one(related="user_input_id.survey_id")
    partner_id = fields.Many2one(related="user_input_id.partner_id")
    patient_id = fields.Many2one("ni.patient", readonly=True)
    question_id = fields.Many2one(
        "survey.question", string="Question", readonly=True, index=True
    )
    page_id = fields.Many2one(related="question_id.page_id")
    question_sequence = fields.Integer(related="question_id.sequence")
    # answer
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
    # scoring
    answer_score = fields.Float("Score", readonly=True)
    answer_is_correct = fields.Boolean("Correct", readonly=True)

    @property
    def _table_query(self):
        return """
                SELECT A.*, latest.patient_id
                FROM survey_user_input_line A
                JOIN (
                    SELECT
                        max(id) AS id,
                        patient_id,
                        survey_id,
                        DATE_TRUNC('month', create_date) AS month
                    FROM survey_user_input
                    WHERE state = 'done'
                    GROUP BY patient_id, survey_id, DATE_TRUNC('month', create_date)
                ) latest ON
                    A.user_input_id = latest.id
                    AND DATE_TRUNC('month', A.create_date) = latest.month
            """

    @api.model
    def _select(self):
        return """
            SELECT
                A.*
        """

    @api.model
    def _from(self):
        return "FROM survey_user_input_line A"

    @api.model
    def _where(self):
        return ""

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"CREATE OR REPLACE VIEW {self._table} AS ({self._table_query})"
        self.env.cr.execute(query)
