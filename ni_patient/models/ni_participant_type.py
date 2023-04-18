#  Copyright (c) 2022-2023 NSTDA

from odoo import fields, models


class ParticipantType(models.Model):
    _name = "ni.participant.type"
    _description = "Participant Type"
    _inherit = "ni.coding"

    limit = fields.Integer(default=-1)
