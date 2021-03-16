#  Copyright (c) 2021 Piruin P.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    active = fields.Boolean(default=True)
    note = fields.Text()
    _codes = []
    _codes_min_max = []

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

    def check_input_range(self, args):
        self.ensure_one()
        for code, _min, _max in args:
            if not (_min <= self[code] <= _max):
                raise ValidationError(
                    _("%s is out of range [%d-%d]")
                    % (self._fields[code].string, _min, _max)
                )
