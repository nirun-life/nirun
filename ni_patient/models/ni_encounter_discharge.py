#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class EncounterDischarge(models.Model):
    _name = "ni.encounter.discharge"
    _description = "Discharge Disposition"
    _inherit = ["ni.coding"]

    deceased = fields.Boolean(
        "Patient Deceased?",
        default=False,
        help="Indicate whether discharged patient was deceased or not",
    )
