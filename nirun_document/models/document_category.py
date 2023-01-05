#  Copyright (c) 2023. NSTDA

from odoo import fields, models


class DocumentCategory(models.Model):
    _name = "ni.document.category"
    _description = "Document Reference Category"
    _inherit = ["coding.base"]

    type_ids = fields.One2many("ni.document.type", "category_id")
