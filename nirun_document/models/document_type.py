#  Copyright (c) 2023. NSTDA

from odoo import fields, models


class DocumentType(models.Model):
    _name = "ni.document.type"
    _description = "Document Reference Type"
    _inherit = ["coding.base"]

    category_id = fields.Many2one("ni.document.category")

    def write(self, vals):
        res = super(DocumentType, self).write(vals)
        if "category_id" in vals:
            doc = self.env["ni.document"].search([("type_id", "in", self.ids)])
            if doc:
                res = res and doc.write({"category_id": vals["category_id"]})
        return res
