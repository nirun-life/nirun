#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class AllergyIntoleranceCode(models.Model):
    _name = "ni.allergy.code"
    _description = "Allergy / Intolerance Code"
    _inherit = ["ni.coding"]

    category = fields.Selection(
        [
            ("food", "Food"),
            ("environment", "Environment"),
            ("biologic", "Biologic"),
            ("medication", "Medication"),
        ],
        required=True,
    )
