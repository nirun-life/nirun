#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class EncounterReason(models.Model):
    _name = "ni.encounter.reason"
    _description = "Encounter Reason"
    _inherit = ["coding.base"]

    encounter_ids = fields.Many2many(
        "ni.encounter",
        "ni_encounter_reason_rel",
        "reason_id",
        "encounter_id",
        readonly=True,
    )
