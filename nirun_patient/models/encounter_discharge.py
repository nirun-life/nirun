#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class EncounterDischarge(models.Model):
    _name = "ni.encounter.discharge"
    _description = "Discharge Disposition"
    _inherit = ["coding.base"]

    deceased = fields.Boolean(
        "Patient Deceased?",
        default=False,
        help="Indicate whether discharged patient was deceased or not",
    )
