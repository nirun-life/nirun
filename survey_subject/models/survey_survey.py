#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    subject_type = fields.Selection(
        [("res.partner", "Partner"), ("res.users", "Users")],
        default="res.partner",
        readonly=False,
        required=True,
        help="Target that can answer the survey",
    )

    def action_survey_subject_wizard(self):
        self.ensure_one()

        ctx = dict(self._context)
        ctx.update({"default_survey_id": self.id})
        action = self.env.ref("survey_subject.survey_subject_action").sudo().read()[0]
        return dict(action, context=ctx)
