#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class DocumentReferenceType(models.Model):
    _name = "ni.document.ref.type"
    _description = "Document Reference Type"
    _inherit = ["ni.coding"]

    category_id = fields.Many2one("ni.document.ref.category")
    content = fields.Selection(
        [("data", "Data"), ("attachment", "Attachment")],
        default="attachment",
        required=True,
        help="Default content type of this document type but not limit to",
    )
    data_template = fields.Html("Template")
