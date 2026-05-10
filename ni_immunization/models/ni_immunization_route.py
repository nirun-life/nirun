#  Copyright (c) 2026 NSTDA
from odoo import models


class ImmunizationRoute(models.Model):
    _name = "ni.immunization.route"
    _description = "Immunization Route"
    _inherit = ["ni.coding"]
