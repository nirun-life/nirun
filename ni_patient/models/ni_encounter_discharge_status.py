#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class EncounterDischargeStatus(models.Model):
    _name = "ni.encounter.discharge.status"
    _description = "Patient Discharge Status"
    _inherit = ["ni.coding"]

    disposition_ids = fields.Many2many(
        "ni.encounter.discharge.disposition",
        "ni_encounter_discharge_status_disposition",
        "status_id",
        "disposition_id",
    )
