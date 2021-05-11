#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    subject_type = fields.Selection(
        [("res.partner", "Partner"), ("res.users", "Users")],
        default="res.partner",
        readonly=True,
        help="Target that can answer the survey",
        states={"draft": [("readonly", False)]},
    )
