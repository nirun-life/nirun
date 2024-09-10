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

    observation_type_id = fields.Many2one(related="survey_id.observation_type_id")
    observation_score_type = fields.Selection(
        related="survey_id.observation_score_type"
    )

    def write(self, vals):
        state = vals.get("state")
        if state and state == "done":
            self._onchange_state_done()
        return super().write(vals)

    def _onchange_state_done(self):
        ob = self.env["ni.observation"]
        for rec in self.filtered_domain([("observation_type_id", "!=", False)]):
            val = {
                "encounter_id": rec.encounter_id.id,
                "patient_id": rec.patient_id.id,
                "occurrence": fields.Datetime.now(),
                "type_id": rec.observation_type_id.id,
                "value_type": rec.observation_type_id.value_type,
                "survey_response_id": rec.id,
            }
            if rec.observation_score_type == "percentage":
                val.update({"value_float": rec.scoring_percentage})
            else:
                val.update(
                    {"value_int": (rec.scoring_percentage / 100) * rec.scoring_total}
                )
            ob.create(val)

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

    def _quizz_grade(self):
        # Override survey_grading.survey.user_input._quizz_grade()
        self.ensure_one()
        if self.grade_ids == 0:
            return None
        if self.subject_model in ["ni.patient", "ni.encounter"]:
            grades = self.grade_ids.grade_for(
                self.patient_id.age, self.patient_id.gender
            )
            for grade in grades:
                if grade.is_cover(self.scoring_percentage):
                    return grade
            return None
        else:
            return super()._quizz_grade()
