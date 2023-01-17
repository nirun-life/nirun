#  Copyright (c) 2023. NSTDA
from odoo import fields, models


class EncounterParticipant(models.Model):
    _inherit = "ni.encounter.participant"

    type = fields.Many2one(groups="base.group_no_one")
    type_id = fields.Many2one(groups="base.group_no_one")
