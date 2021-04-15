#  Copyright (c) 2021 Piruin P.


from odoo import _, api, fields, models


class SurveySubjectWizard(models.TransientModel):
    _inherit = "survey.subject.wizard"

    subject_ni_patient = fields.Many2one("ni.patient", string="Patient")
    subject_ni_encounter = fields.Many2one(
        "ni.encounter",
        string="Encounter",
        domain="[ ('patient_id', '=', subject_ni_patient)]",
    )

    def subject_get(self):
        result = super(SurveySubjectWizard, self).subject_get()
        if result:
            result.update(
                {
                    "patient_id": self.subject_ni_patient.id,
                    "encounter_id": self.subject_ni_encounter.id,
                }
            )
            return result
        else:
            return {}

    @api.onchange("subject_ni_patient")
    def onchange_patient(self):
        if self.subject_ni_encounter.patient_id != self.subject_ni_patient:
            self.subject_ni_encounter = self.subject_ni_patient.encountering_id

        if self.subject_ni_patient.deceased:
            warning = {
                "title": _("Warning!"),
                "message": _(
                    "%s is already deceased. Reference to this patient may "
                    "cause database inconsistency!"
                )
                % self.subject_ni_patient.name,
            }
            return {"warning": warning}
