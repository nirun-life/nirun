#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class ObservationBase(models.Model):
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
        required=True, default=lambda _: fields.Datetime.now(), index=True
    )
    active = fields.Boolean(default=True)
    note = fields.Text()
    lines = fields.One2many("ni.observation.line", "observation_id")
