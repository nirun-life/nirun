#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class DocumentReferenceCategory(models.Model):
    _name = "ni.document.ref.category"
    _description = "Document Reference Category"
    _inherit = ["ni.coding"]

    type_ids = fields.One2many("ni.document.ref.type", "category_id")
