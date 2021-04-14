#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models, tools


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    @api.model
    def _select_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    subject_model = fields.Char(
        readonly=True, help="The database object be subject of this answer"
    )
    subject_id = fields.Many2oneReference(
        model_field="subject_model",
        readonly=True,
        help="The record id that be subject of this answer",
    )
    subject_ref = fields.Reference(
        selection=_select_target_model,
        string="Subject",
        compute="_compute_subject_ref",
        readonly=True,
        help="The subject of the questions",
    )

    def _auto_init(self):
        res = super(SurveyUserInput, self)._auto_init()
        tools.create_index(
            self._cr,
            "survey_user_input_subject_idx",
            self._table,
            ["subject_model", "subject_id"],
        )
        return res

    @api.depends("subject_model", "subject_id")
    def _compute_subject_ref(self):
        for rec in self:
            rec.subject_ref = (
                "{},{}".format(rec.subject_model, rec.subject_id)
                if rec.subject_model and rec.subject_id
                else None
            )
