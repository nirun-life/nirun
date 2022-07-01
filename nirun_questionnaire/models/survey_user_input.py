#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class SurveyUserInput(models.Model):
    _name = "survey.user_input"
    _inherit = ["survey.user_input", "ni.patient.res"]

    patient_id = fields.Many2one(required=False, groups="nirun_patient.group_user")
    encounter_id = fields.Many2one(required=False, groups="nirun_patient.group_user")

    # FIXME partner_id not set as store. need to find when/why it was changed
    partner_id = fields.Many2one(store=True)

    def init(self):
        tools.create_index(
            self._cr,
            "survey_user_input__patient_survey__idx",
            self._table,
            ["patient_id", "survey_id"],
        )

        tools.create_index(
            self._cr,
            "survey_user_input__encounter_survey__idx",
            self._table,
            ["encounter_id", "survey_id"],
        )

    def name_get(self):
        res = []
        for survey_input in self:
            name = survey_input._get_name()
            res.append((survey_input.id, name))
        return res

    def _get_name(self):
        survey_input = self
        name = "%s" % survey_input.create_date.strftime("%Y-%m-%d")
        if survey_input.survey_id.scoring_type != "no_scoring":
            name = "{} | {}%".format(name, survey_input.quizz_score)
        if survey_input.quizz_grade_id:
            name = "{} ({})".format(
                name,
                survey_input.quizz_grade_id.display_name,
            )
        if self.env.context.get("show_survey"):
            name = "{}: {}".format(survey_input.survey_id.display_name, name)
        return name

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
                "graph_view_ref": "nirun_questionnaire.survey_user_input_view_graph",
            },
            "views": [[False, "graph"]],
        }
