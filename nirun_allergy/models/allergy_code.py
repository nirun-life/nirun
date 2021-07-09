#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class AllergyIntoleranceCode(models.Model):
    _name = "ni.allergy.code"
    _description = "Allergy / Intolerance Code"
    _inherit = ["coding.base"]

    category = fields.Selection(
        [("food", "Food"), ("environment", "Environment"), ("biologic", "Biologic")],
        required=True,
    )
