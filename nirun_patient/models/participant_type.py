#  Copyright (c) 2022-2023. NSTDA

from odoo import fields, models


class ParticipantType(models.Model):
    _name = "ni.participant.type"
    _description = "Participant Type"
    _inherit = "coding.base"

    limit = fields.Integer(default=-1)
