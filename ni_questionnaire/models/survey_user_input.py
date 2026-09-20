#  Copyright (c) 2021-2023. NSTDA

from odoo import _, api, fields, models, tools
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

    def init(self):
        super().init()
        tools.create_index(
            self._cr,
            "survey_user_input_patient_survey_create_date_idx",
            self._table,
            ["patient_id", "survey_id", "create_date DESC", "id"],
            where="state = 'done' AND patient_id IS NOT NULL",
        )
        tools.create_index(
            self._cr,
            "survey_user_input_encounter_survey_create_date_idx",
            self._table,
            ["encounter_id", "survey_id", "create_date DESC", "id"],
            where="state = 'done' AND encounter_id IS NOT NULL",
        )

    def _mark_done(self):
        # After super(): _mark_done() drops the inactive conditional questions from
        # predefined_question_ids, which is what shrinks scoring_percentage's maximum.
        # Reading the score any earlier snapshots the pre-trim value.
        res = super()._mark_done()
        self._create_survey_observations()
        return res

    def _create_survey_observations(self):
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
                    "occurrence": rec.create_date,
                }
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
            "occurrence": self.create_date,
        }

    @staticmethod
    def _score_observation(rec):
        code = rec.observation_type_id
        val = rec._base_observation(code)
        if rec.observation_score_type == "percentage":
            result = rec.scoring_percentage
        else:
            result = rec.scoring_total

        if code.value_type == "float":
            val.update({"value": str(result)})
        elif code.value_type == "int":
            val.update({"value": str(int(result))})
        else:
            raise ValidationError(
                _("{} value type is [{}], not support score input").format(
                    code.name, code.value_type
                )
            )
        return val

    @staticmethod
    def _answer_line_observation(_input, line):
        question = line.question_id
        code = question.observation_code_id
        if not code:
            return None
        val = _input._base_observation(code)

        if question.observation_answer_type != "value":
            if code.value_type == "int":
                val.update({"value": str(int(line.answer_score))})
            elif code.value_type == "float":
                val.update({"value": str(line.answer_score)})
            else:
                raise ValidationError(
                    _("{} value type is [{}], not support score input").format(
                        code.name, code.value_type
                    )
                )
        else:
            # Dispatch on answer_type, not on truthiness: a numerical answer of 0 is
            # a real answer, and datetime questions have no truthy alias here.
            if line.suggested_answer_id:
                answer = line.suggested_answer_id.value
            elif line.answer_type == "date":
                answer = line.value_date
            elif line.answer_type == "datetime":
                answer = line.value_datetime
            elif line.answer_type == "char_box":
                answer = line.value_char_box
            elif line.answer_type == "text_box":
                answer = line.value_text_box
            elif line.answer_type == "numerical_box":
                answer = line.value_numerical_box
            else:
                raise ValidationError(_("Not support this type of answer"))
            val.update({"value": str(answer)})
        return val

    @staticmethod
    def _answer_group_observation(_input, group):
        code = group.observation_code_id
        val = _input._base_observation(code)

        lines = _input.user_input_line_ids.filtered_domain(
            [("question_id", "in", group.question_ids.ids), ("skipped", "=", False)]
        )
        if not lines:
            # Every question of the group was hidden by a conditional display
            return None

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
            val.update({"value": str(int(result))})
        elif code.value_type == "float":
            val.update({"value": str(result)})
        else:
            raise ValidationError(
                _("{} value type is [{}], not support score input").format(
                    code.observation_type_id.name, code.observation_type_id.value_type
                )
            )
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
        domain = [("survey_id", "=", self.survey_id.id), ("test_entry", "=", False)]
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
                "search_default_completed": 1,
                "graph_view_ref": "ni_questionnaire.survey_user_input_view_graph",
            },
            "views": [[False, "graph"]],
        }

    def action_monthly_pivot_view(self):
        self.ensure_one()
        domain = [("survey_id", "=", self.survey_id.id)]
        if self.survey_id.subject_type in ["ni.patient", "ni.encounter"]:
            domain.append(("patient_id", "=", self.patient_id.id))
        return {
            "type": "ir.actions.act_window",
            "name": self.survey_id.title,
            "res_model": "survey.user_input.line.monthly.report",
            "view_mode": "pivot",
            "target": "current",
            "domain": domain,
            "context": {
                "pivot_view_ref": "ni_questionnaire.survey_user_input_line_monthly_report_view_pivot",
            },
            "views": [[False, "pivot"]],
        }

    def _grade_candidates(self):
        # Override survey_grading.survey.user_input._grade_candidates()
        grades = super()._grade_candidates()
        if self.subject_model in ["ni.patient", "ni.encounter"]:
            return grades.grade_for(self.patient_id.age, self.patient_id.gender)
        return grades

    def grade_conditions(self):
        # Override survey_grading.survey.user_input.grade_conditions(): name the
        # patient traits grade_for() selected on, but only the ones this survey
        # actually grades differently by - otherwise every result page would carry
        # an age and a gender that had no bearing on the grade.
        res = super().grade_conditions()
        if self.subject_model not in ["ni.patient", "ni.encounter"]:
            return res
        grades = self.grade_ids
        patient = self.patient_id
        if patient.gender and any(grades.mapped("gender")):
            selection = grades._fields["gender"]._description_selection(self.env)
            res.append(dict(selection)[patient.gender])
        if len(set(grades.mapped(lambda g: (g.age_low, g.age_high)))) > 1:
            res.append(_("Age %s") % patient.age)
        return res
