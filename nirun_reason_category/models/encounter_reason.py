#  Copyright (c) 2021-2023. NSTDA

from odoo import fields, models


class EncounterReason(models.Model):
    _name = "ni.encounter.reason"
    _description = "Encounter Reason"
    _inherit = ["coding.base"]

    category_id = fields.Many2one("ni.encounter.reason.category")
    color = fields.Integer(related="category_id.color", readonly=False)
