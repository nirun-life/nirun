#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import SQL


class SurveySubjectWizard(models.TransientModel):
    _inherit = "survey.subject.wizard"

    retrospective = fields.Boolean()
    survey_date = fields.Datetime()

    def subject_get(self):
        res = super().subject_get()
        if self.retrospective:
            res.update({"retrospective": True})
        return res

    def _create_answer(self):
        answer = super()._create_answer()
        if self.retrospective:
            self.env.cr.execute(
                SQL(
                    "UPDATE survey_user_input SET create_date = %s WHERE id = %s",
                    self.survey_date,
                    answer.id,
                )
            )
            answer.invalidate_recordset(["create_date"])
        return answer

    @api.constrains("retrospective", "survey_date")
    def check_survey_date(self):
        if self.retrospective and not self.survey_date:
            raise ValidationError(self.env._("Survey date is require!"))
        if self.survey_date and self.survey_date >= fields.Datetime.now():
            raise ValidationError(self.env._("Survey date must not be in future!"))
