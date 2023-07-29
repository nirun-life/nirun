#  Copyright (c) 2023. NSTDA

from odoo import models


class CommunicationCategory(models.Model):
    _name = "ni.communication.category"
    _description = "Communication Category"
    _inherit = ["ni.coding"]
