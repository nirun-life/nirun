#  Copyright (c) 2023. NSTDA

from odoo import fields, models


class CommunicationContent(models.Model):
    _name = "ni.communication.content"
    _description = "Communication Content"
    _inherit = ["ni.coding"]

    category_id = fields.Many2one(
        "ni.communication.category",
        ondelete="set null",
        help="Default category for code but not limit to.",
    )
