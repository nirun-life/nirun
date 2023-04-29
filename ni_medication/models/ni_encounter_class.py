#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter.class"

    medication_category_id = fields.Many2one(
        "ni.medication.admin.location",
        help="Default category for Medication Request of this encounter class",
    )
