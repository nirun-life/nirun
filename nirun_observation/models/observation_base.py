#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


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
    _codes = []

    @api.depends(lambda self: self._codes)
    def _compute_interpretation(self):
        for rec in self:
            for code in self._codes:
                rec["%s_interpretation_id" % code] = rec._interpretation_for(code)

    def _interpretation_for(self, code):
        if not self[code]:
            return None

        ranges = self.env["ni.observation.reference.range"].match_for(
            observation=code, value=self[code]
        )
        return (
            ranges[0].interpretation_id
            if ranges
            else self.env.ref("nirun_observation.interpretation_EX")
        )
