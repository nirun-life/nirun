#  Copyright (c) 2021 NSTDA

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SurveySubjectWizard(models.TransientModel):
    _inherit = "survey.subject.wizard"
    _description = "Survey Subject Wizard"

    retrospective = fields.Boolean()
    survey_date = fields.Datetime()

    def subject_get(self):
        res = super(SurveySubjectWizard, self).subject_get()
        if self.retrospective:
            res.update({"retrospective": True})
        return res

    def action_survey(self):
        answer = self.sudo().survey_id._create_answer(
            user=self.env.user, **self.subject_get()
        )
        if self.retrospective:
            self.env.cr.execute(
                "UPDATE survey_user_input SET create_date = %s WHERE id = %s",
                (self.survey_date.strftime("%Y-%m-%d %H:%M:%S"), answer.id),
            )
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": "{}?answer_token={}".format(self.survey_id.public_url, answer.token),
        }

    @api.constrains("retrospective", "survey_date")
    def check_survey_date(self):
        if self.retrospective and not self.survey_date:
            raise ValidationError(_("Survey date is require!"))
        if self.survey_date and self.survey_date >= fields.Datetime.now():
            raise ValidationError(_("Survey date must not be in future!"))
