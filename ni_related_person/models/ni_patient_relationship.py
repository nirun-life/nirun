#  Copyright (c) 2024 NSTDA
from odoo import models


class PatientRelationship(models.Model):
    _name = "ni.patient.relationship"
    _description = "Patient Relationship"
    _inherit = "ni.coding"
