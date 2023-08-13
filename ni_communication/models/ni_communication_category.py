#  Copyright (c) 2023. NSTDA

from odoo import fields, models


class CommunicationCategory(models.Model):
    _name = "ni.communication.category"
    _description = "Communication Category"
    _inherit = ["ni.coding"]

    content_ids = fields.One2many("ni.communication.content", "category_id")
