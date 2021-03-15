#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class ObservationBase(models.AbstractModel):
    _name = "ni.observation.base"
    _description = "Observation"
    _inherit = ["ni.patient.res"]

    patient_age_years = fields.Integer(related="patient_id.age_years")
    performer_ref = fields.Reference(
        [("ni.patient", "Patient"), ("hr.employee", "Practitioner")],
        required=False,
        index=True,
    )
    effective_date = fields.Datetime(
        required=True, default=lambda _: fields.Datetime.now()
    )
    note = fields.Text()

    def interpretation_for(self, field):
        self.ensure_one()
        ref_range = self.env["ni.observation.reference.range"].match_for(
            field, self[field]
        )
        return ref_range[0].interpretation_id if ref_range else None
