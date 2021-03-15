#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class ObservationBase(models.AbstractModel):
    _name = "ni.observation.base"
    _description = "Observation"

    company_id = fields.Many2one(
        "res.company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    patient_id = fields.Many2one(
        "ni.patient", index=True, required=True, ondelete="cascade", check_company=True,
    )
    patient_age_years = fields.Integer(related="patient_id.age_years")
    encounter_id = fields.Many2one("ni.encounter", index=True, require=False)
    performer_ref = fields.Reference(
        [("ni.patient", "Patient"), ("hr.employee", "Practitioner")],
        required=False,
        index=True,
    )
    effective_date = fields.Datetime(default=lambda _: fields.Datetime.now())
    note = fields.Text()
