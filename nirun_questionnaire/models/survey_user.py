#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SurveyUserInput(models.Model):
    _name = "survey.user_input"
    _inherit = ["survey.user_input", "ni.patient.res"]

    patient_id = fields.Many2one(required=False, groups="nirun_patient.group_user")
    encounter_id = fields.Many2one(required=False, groups="nirun_patient.group_user")

    # FIXME partner_id not set as store. need to find when/why it was changed
    partner_id = fields.Many2one(store=True)

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
