#  Copyright (c) 2021-2023. NSTDA

from odoo import fields, models


class EncounterReasonCategory(models.Model):
    _name = "ni.encounter.reason.category"
    _description = "Encounter Reason Category"
    _inherit = ["coding.base"]

    encounter_ids = fields.Many2many(
        "ni.encounter",
        "ni_encounter_reason_rel",
        "reason_id",
        "encounter_id",
        readonly=True,
    )
