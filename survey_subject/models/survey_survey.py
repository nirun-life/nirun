#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    subject_type = fields.Selection(
        [("res.partner", "Partner"), ("res.users", "Users")],
        default="res.partner",
        readonly=True,
        help="Target that can answer the survey",
        states={"draft": [("readonly", False)]},
    )

    def action_survey_subject_wizard(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx.update({"default_survey_id": self.id})
        action = self.env["ir.actions.act_window"].for_xml_id(
            "survey_subject", "survey_subject_action"
        )
        return dict(action, context=ctx)
