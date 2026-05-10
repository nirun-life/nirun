#  Copyright (c) 2026 NSTDA
from odoo import models


class ImmunizationVaccine(models.Model):
    _name = "ni.immunization.vaccine"
    _description = "Vaccine"
    _inherit = ["ni.coding"]
