#  Copyright (c) 2021 Piruin P.

from odoo import models


class PatientRelationship(models.Model):
    _name = "res.partner.relationship"
    _description = "Relationship"
    _inherit = ["coding.base"]
