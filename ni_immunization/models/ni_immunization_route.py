#  Copyright (c) 2026 NSTDA
from odoo import fields, models


class ImmunizationRoute(models.Model):
    _name = "ni.immunization.route"
    _description = "Immunization Route"
    _inherit = ["ni.coding"]

    site_ids = fields.Many2many(
        "ni.body.site",
        "ni_immunization_route_body_site",
        "route_id",
        "site_id",
        string="Injection Sites",
    )
