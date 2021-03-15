#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models


class PatientRes(models.AbstractModel):
    _name = "ni.patient.res"
    _description = "Patient Resource"
    _check_company_auto = True

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "PatientRes",
        store=True,
        index=True,
        ondelete="cascade",
        required=True,
        check_company=True,
    )
    encounter_id = fields.Many2one(
        "ni.encounter",
        "Encounter",
        ondelete="restrict",
        index=True,
        check_company=True,
        domain="""[
              ('patient_id', '=', patient_id),
              ('state', 'in', ['draft','planned','in-progress'])
          ]""",
    )

    @api.onchange("patient_id")
    def onchange_patient(self):
        self.encounter_id = self.patient_id.current_encounter_id

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
