#  Copyright (c) 2022. NSTDA

from odoo import fields, models


class ParticipantType(models.Model):
    _name = "ni.participant.type"
    _inherit = "coding.base"

    limit = fields.Integer(default=-1)
