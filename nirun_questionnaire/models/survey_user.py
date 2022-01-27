#  Copyright (c) 2021 Piruin P.

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

    def name_get(self):
        res = []
        for survey_input in self:
            name = survey_input._get_name()
            res.append((survey_input.id, name))
        return res

    def _get_name(self):
        survey_input = self
        name = "%s" % survey_input.survey_id.display_name
        if self.env.context.get("show_grade") and survey_input.quizz_grade_id:
            name = "{}/{}".format(name, survey_input.quizz_grade_id.display_name)
        if self.env.context.get("show_patient") and survey_input.patient_id:
            name = "{}: {}".format(survey_input.patient_id.display_name, name)
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
