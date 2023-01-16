#  Copyright (c) 2023. NSTDA
from odoo import _, api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    birthdate_estimate = fields.Boolean(
        "Estimate Date of Birth",
        default=False,
        required=True,
        help="Indicate whether input birthday is estimated value, "
        "Exactly date of birth is unknown.",
    )

    _sql_constraints = [
        (
            "birthdate_estimate_check",
            """CHECK (
                birthdate_estimate is FALSE or
                birthdate_estimate is NULL or
                (birthdate_estimate is TRUE and EXTRACT(DAY FROM birthdate) = 1)
            )""",
            _("Birth date must be 1 January"),
        ),
    ]

    @api.onchange("birthdate_estimate")
    def onchange_birthdate_estimate(self):
        if self.birthdate_estimate:
            date = self.birthdate or fields.Date.today()
            self.birthdate = date.replace(month=1, day=1)
