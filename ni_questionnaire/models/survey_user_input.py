#  Copyright (c) 2021-2023. NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    company_id = fields.Many2one(
        "res.company", related="patient_id.company_id", required=False, store=True
    )
    patient_id = fields.Many2one("ni.patient", required=False)
    encounter_id = fields.Many2one("ni.encounter", required=False)

    @api.constrains("encounter_id")
    def check_encounter_id(self):
        for rec in self:
            if rec.encounter_id and rec.patient_id != rec.encounter_id.patient_id:
                raise ValidationError(
                    _("The referencing encounter is not belong to patient")
                )

    def action_survey_subject_wizard(self):
        res = super(SurveyUserInput, self).action_survey_subject_wizard()
        if self.survey_id.category in ["ni_patient", "ni_encounter"]:
            res["context"].update(
                {
                    "default_subject_ni_patient": self.patient_id.id,
                    "default_subject_ni_encounter": self.patient_id.encounter_id.id,
                }
            )
        return res

    def action_graph_view(self):
        self.ensure_one()
        domain = [("test_entry", "=", False)]
        if self.survey_id.category in ["ni_patient", "ni_encounter"]:
            domain.append(("patient_id", "=", self.patient_id.id))
        return {
            "type": "ir.actions.act_window",
            "name": self.survey_id.title,
            "res_model": "survey.user_input",
            "view_mode": "graph",
            "target": "current",
            "domain": domain,
            "context": {
                "search_default_survey_id": self.survey_id.id,
                "search_default_completed": 1,
                "graph_view_ref": "ni_questionnaire.survey_user_input_view_graph",
            },
            "views": [[False, "graph"]],
        }
