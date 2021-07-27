#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    birthdate_estimate = fields.Boolean(
        "Estimate Date of Birth",
        default=False,
        help="Indicate whether input birthday is estimated value, "
        "Exactly date of birth is unknown.",
    )
