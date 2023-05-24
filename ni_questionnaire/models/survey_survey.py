#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    subject_type = fields.Selection(
        selection=[
            ("res.partner", "Partner"),
            ("res.users", "Users"),
            ("ni.patient", "Patient"),
            ("ni.encounter", "Encounter"),
        ],
    )
