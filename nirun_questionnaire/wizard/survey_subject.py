#  Copyright (c) 2021 Piruin P.


from odoo import _, api, fields, models


class SurveySubjectWizard(models.TransientModel):
    _inherit = "survey.subject.wizard"

    subject_ni_patient = fields.Many2one("ni.patient", string="Patient")
    subject_ni_encounter = fields.Many2one(
        "ni.encounter",
        string="Encounter",
        domain="[ ('patient_id', '=?', subject_ni_patient)]",
    )

    @api.onchange("subject_ni_encounter")
    def onchange_encounter(self):
        for rec in self.filtered(lambda r: r.subject_ni_encounter):
            if rec.subject_ni_patient != rec.subject_ni_encounter.patient_id:
                rec.subject_ni_patient = rec.subject_ni_encounter.patient_id

    @api.onchange("subject_ni_patient")
    def onchange_patient(self):
        for rec in self.filtered(lambda r: r.subject_ni_patient):
            if rec.subject_ni_encounter.patient_id != rec.subject_ni_patient:
                rec.subject_ni_encounter = rec.subject_ni_patient.encounter_id

            if rec.subject_ni_patient.deceased:
                warning = {
                    "title": _("Warning!"),
                    "message": _(
                        "%s is already deceased. Reference to this patient may "
                        "cause database inconsistency!"
                    )
                    % rec.subject_ni_patient.name,
                }
                return {"warning": warning}

    def subject_get(self):
        result = super(SurveySubjectWizard, self).subject_get()
        if result:
            result.update(
                {
                    "partner_id": self.subject_ni_patient.partner_id.id,
                    "patient_id": self.subject_ni_patient.id,
                    "encounter_id": self.subject_ni_encounter.id,
                }
            )
            return result
        else:
            return {}
