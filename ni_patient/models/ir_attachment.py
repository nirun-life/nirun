#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    # Deleting an attachment checks this ON DELETE SET NULL foreign key.
    original_id = fields.Many2one(index="btree_not_null")
