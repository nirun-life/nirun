#  Copyright (c) 2021 Piruin P.

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SurveySubjectWizard(models.TransientModel):
    _name = "survey.subject.wizard"
    _description = "Survey Subject Wizard"

    @api.model
    def _select_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    survey_id = fields.Many2one("survey.survey", required=True)
    type = fields.Char(
        compute="_compute_type",
        readonly=True,
        help="subject's model name of current survey",
    )

    subject_res_partner = fields.Many2one("res.partner", string="Partner")
    subject_res_users = fields.Many2one("res.users", string="User")

    @api.depends("survey_id")
    def _compute_type(self):
        for rec in self:
            rec.type = rec.survey_id.subject_type

    def subject_get(self):
        try:
            subject_field = "subject_" + self.type.replace(".", "_")
            subject = getattr(self, subject_field)
        except AttributeError:
            _logger.error(self.type + ": Not found field value for this subject type")
            raise ValidationError(
                _("%s : Not found field value for this subject type") % self.type
            )
        else:
            if not subject:
                raise ValidationError(
                    _("Please select %s") % self._fields[subject_field].string
                )
            return {"subject_model": self.type, "subject_id": subject.id}

    def action_survey(self):
        answer = self.survey_id._create_answer(user=self.env.user, **self.subject_get())
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": "{}?answer_token={}".format(self.survey_id.public_url, answer.token),
        }