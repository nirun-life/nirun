#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class EncounterDischargeDisposition(models.Model):
    _name = "ni.encounter.discharge.disposition"
    _description = "Patient Discharge Disposition"
    _inherit = ["ni.coding"]

    deceased = fields.Boolean(
        "Patient Deceased?",
        default=False,
        help="Indicate whether discharged patient was deceased or not",
    )
    referral = fields.Boolean(
        default=False,
        help="Indicate whether patient was refer to other organization or not",
    )
    status_ids = fields.Many2many(
        "ni.encounter.discharge.status",
        "ni_encounter_discharge_status_disposition",
        "disposition_id",
        "status_id",
    )
