#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ObservationAbstract(models.AbstractModel):
    _inherit = "ni.observation.abstract"

    survey_id = fields.Many2one(related="type_id.survey_id")
    survey_response_id = fields.Many2one(
        "survey.user_input",
        "Derived From Survey",
        store=True,
        groups="survey.group_survey_user",
    )

    @api.depends("value", "survey_response_id.grade_id")
    def _compute_interpretation(self):
        return super()._compute_interpretation()

    def _interpretation_for(self):
        """A grade may carry its own interpretation.

        A questionnaire whose maximum score varies between responses cannot be read
        against the observation type's reference ranges, which only scope by age and
        gender. sudo() because survey_response_id is restricted to survey users.
        """
        grade = self.sudo().survey_response_id.grade_id
        if grade.interpretation_id:
            return grade.interpretation_id
        return super()._interpretation_for()

    def action_print_survey(self):
        """If response is available then print this response otherwise print
        survey form (print template of the survey)"""
        self.ensure_one()
        if self.survey_response_id:
            action = self.survey_response_id.survey_id.action_print_survey(
                self.survey_response_id
            )
            action["target"] = "new"
            return action

    def action_survey_subject(self):
        self.ensure_one()
        if not self.survey_id:
            raise ValidationError(_("This observation not have survey"))

        if "patient_id" in self._fields and self["patient_id"]:
            enc = self.patient_id.encounter_id
            # enc = self.env['ni.encounter'].browse(self._context.get('active_id'))
            if enc:
                action = enc[0].action_survey_subject()
                ctx = dict(action.get("context"))
            else:
                action_rec = self.env.ref("survey_subject.survey_subject_action").sudo()
                action = action_rec.read()[0]
                ctx = dict(self.env.context)
                ctx.update({"default_subject_ni_patient": self.patient_id.id})
            def_val = {"default_survey_id": self.survey_id.id}
            ctx.update(def_val)
            action["context"] = ctx
            return action

        raise ValidationError(
            _("Can't start survey! This may cause by misconfiguration")
        )
