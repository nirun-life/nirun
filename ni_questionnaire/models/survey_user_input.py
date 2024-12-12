#  Copyright (c) 2021-2023. NSTDA
import pprint

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
    observation_group_ids = fields.One2many(related="survey_id.question_group_ids")

    def write(self, vals):
        state = vals.get("state")
        if state and state == "done":
            self._onchange_state_done()
        return super().write(vals)

    def _onchange_state_done(self):
        for rec in self:
            vals = []
            if rec.observation_type_id:
                vals.append(self._score_observation(rec))

            for line in rec.user_input_line_ids.filtered_domain(
                [("skipped", "=", False)]
            ):
                vals.append(self._answer_line_observation(rec, line))

            for grp in rec.observation_group_ids:
                vals.append(self._answer_group_observation(rec, grp))
            vals = [val for val in vals if val is not None]
            if len(vals) > 1:
                sheet_val = {
                    "encounter_id": rec.encounter_id.id,
                    "patient_id": rec.patient_id.id,
                    "observation_ids": [fields.Command.create(val) for val in vals],
                }
                pprint.pprint(sheet_val)
                self.env["ni.observation.sheet"].create(sheet_val)
            elif len(vals) == 1:
                self.env["ni.observation"].create(vals)

    def _base_observation(self, code):
        return {
            "encounter_id": self.encounter_id.id,
            "patient_id": self.patient_id.id,
            "type_id": code.id,
            "value_type": code.value_type,
            "survey_response_id": self.id,
        }

    @staticmethod
    def _score_observation(rec):
        val = rec._base_observation(rec.observation_type_id)
        if rec.observation_score_type == "percentage":
            result = rec.scoring_percentage
        else:
            result = rec.scoring_total

        if rec.observation_type_id.value_type == "float":
            val.update({"value_float": result})
        elif rec.observation_type_id.value_type == "int":
            val.update({"value_int": int(result)})
        else:
            val.update({"value": str(result)})
        return val

    @staticmethod
    def _answer_line_observation(_input, line):
        question = line.question_id
        code = question.observation_code_id
        if not code:
            return None
        val = _input._base_observation(code)

        if question.observation_answer_type == "score":
            if code.value_type == "int":
                val.update({"value_int": int(line.answer_score)})
            elif code.value_type == "float":
                val.update({"value_float": line.answer_score})
            else:
                raise ValidationError(
                    _("{} value type is [{}], not support score input").format(
                        code.name, code.value_type
                    )
                )
        elif question.observation_answer_type == "value":
            if line.suggested_answer_id:
                val.update({"value": line.suggested_answer_id.value})
            elif line.value_date:
                val.update({"value": str(line.value_date)})
            elif line.value_char_box:
                val.update({"value_char": line.value_char_box})
            elif line.value_text_box:
                val.update({"value_char": line.value_text_box})
            elif line.value_numerical_box:
                val.update({"value": str(line.value_numerical_box)})
            else:
                raise ValidationError(_("Not support this type of answer"))
        return val

    @staticmethod
    def _answer_group_observation(_input, group):
        code = group.observation_code_id
        val = _input._base_observation(code)

        lines = _input.user_input_line_ids.filtered_domain(
            [("question_id", "in", group.question_ids.ids), ("skipped", "=", False)]
        )
        result = 0
        if group.operator == "sum":
            result = sum(lines.mapped("answer_score"))
        if group.operator == "avg":
            result = sum(lines.mapped("answer_score")) / len(lines)
        if group.operator == "min":
            result = min(lines.mapped("answer_score"))
        if group.operator == "max":
            result = max(lines.mapped("answer_score"))

        if code.value_type == "int":
            val.update({"value_int": int(result)})
        elif code.value_type == "float":
            val.update({"value_float": result})
        return val

    @api.constrains("encounter_id")
    def check_encounter_id(self):
        for rec in self:
            if rec.encounter_id and rec.patient_id != rec.encounter_id.patient_id:
                raise ValidationError(
                    _("The referencing encounter is not belong to patient")
                )

    def action_survey_subject_wizard(self):
        res = super(SurveyUserInput, self).action_survey_subject_wizard()
        if self.survey_id.subject_type in ["ni.patient", "ni.encounter"]:
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
        if self.survey_id.subject_type in ["ni.patient", "ni.encounter"]:
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
