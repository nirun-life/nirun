#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class EncounterReason(models.Model):
    _name = "ni.encounter.reason"
    _description = "Encounter Reason"
    _inherit = ["ni.coding"]

    encounter_ids = fields.Many2many(
        "ni.encounter",
        "ni_encounter_reason_rel",
        "reason_id",
        "encounter_id",
        readonly=True,
    )
