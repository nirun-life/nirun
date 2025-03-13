#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class PatientResource(models.AbstractModel):
    _inherit = "ni.patient.res"

    state_id = fields.Many2one(related="patient_id.state_id", store=True, index=True)
    city_id = fields.Many2one(related="patient_id.city_id", store=True, index=True)
