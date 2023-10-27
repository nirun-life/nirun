#  Copyright (c) 2021-2023 NSTDA

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
        except AttributeError as err:
            _logger.error(self.type + ": Not found field value for this subject type")
            raise ValidationError(
                _("%s : Not found field value for this subject type") % self.type
            ) from err
        else:
            if not subject:
                raise ValidationError(
                    _("Please select %s") % self._fields[subject_field].string
                )
            return {"subject_model": self.type, "subject_id": subject.id}

    def action_survey(self):
        answer = self.sudo().survey_id._create_answer(
            user=self.subject_res_users or self.env.user,
            partner=self.subject_res_partner,
            **self.subject_get()
        )
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": "/survey/start/%s?answer_token=%s"
            % (self.survey_id.access_token, answer.access_token),
            "close_on_report_download": True,
        }
