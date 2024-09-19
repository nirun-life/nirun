from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SurveyQuestionGroup(models.Model):
    _name = "survey.question.group"
    _description = "Survey answer group"
    _order = "sequence"

    sequence = fields.Integer()
    survey_id = fields.Many2one("survey.survey", required=True)
    question_ids = fields.Many2many(
        "survey.question", required=True, domain="[('survey_id', '=', survey_id)]"
    )
    observation_code_id = fields.Many2one(
        "ni.observation.type",
        "Observation",
        required=True,
        domain="[('value_type', 'in', ['int', 'float'])]",
    )
    operator = fields.Selection(
        [
            ("sum", "Summary"),
            ("avg", "Average"),
            ("min", "Minimum"),
            ("max", "Maximum"),
        ],
        default="sum",
        required=True,
    )

    @api.constrains("question_ids")
    def _check_question(self):
        for rec in self:
            if len(rec.question_ids) < 2:
                raise UserError(_("Must specify at least 2 question"))
