#  Copyright (c) 2023 NSTDA
from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    birthdate_estimate = fields.Boolean(
        "Estimate Date of Birth",
        default=False,
        help="Indicate whether input birthday is estimated value, "
        "Exactly date of birth is unknown.",
    )

    _birthdate_estimate_check = models.Constraint(
        "CHECK (\n                birthdate_estimate is FALSE or\n                birthdate_estimate is NULL or\n                (birthdate_estimate is TRUE and EXTRACT(DAY FROM birthdate) = 1)\n            )",
        "Birth date must be 1 January",
    )
