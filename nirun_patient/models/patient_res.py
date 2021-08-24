#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models


class PatientRes(models.AbstractModel):
    _name = "ni.patient.res"
    _description = "Patient Resource"
    _check_company_auto = True

    company_id = fields.Many2one(
        related="patient_id.company_id", store=True, readonly=True, index=True
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        store=True,
        index=True,
        ondelete="cascade",
        required=True,
        check_company=True,
    )
    partner_id = fields.Many2one(related="patient_id.partner_id")
    encounter_id = fields.Many2one(
        "ni.encounter",
        "Encounter No.",
        ondelete="restrict",
        index=True,
        check_company=True,
        domain="""[
              ('patient_id', '=?', patient_id),
              ('state', 'in', ['draft','planned','in-progress'])
          ]""",
    )

    @api.onchange("patient_id")
    def onchange_patient(self):
        if self.encounter_id.patient_id != self.patient_id:
            self.encounter_id = self.patient_id.encountering_id

        if self.patient_id.deceased:
            warning = {
                "title": _("Warning!"),
                "message": _(
                    "%s is already deceased. Reference to this patient may "
                    "cause database inconsistency!"
                )
                % self.patient_id.name,
            }
            return {"warning": warning}

    @api.onchange("encounter_id")
    def onchange_encounter(self):
        if self.encounter_id and (self.patient_id != self.encounter_id.patient_id):
            self.patient_id = self.encounter_id.patient_id
