#  Copyright (c) 2026 NSTDA
from odoo import fields, models


class ImmunizationVaccine(models.Model):
    _name = "ni.immunization.vaccine"
    _description = "Vaccine"
    _inherit = ["ni.coding"]

    target_disease_ids = fields.Many2many(
        "ni.immunization.target.disease",
        "ni_immunization_vaccine_disease",
        "vaccine_id",
        "disease_id",
        string="Target Diseases",
    )
