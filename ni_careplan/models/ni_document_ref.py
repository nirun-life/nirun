#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class DocumentRef(models.Model):
    _inherit = "ni.document.ref"

    careplan_id = fields.Many2one(
        "ni.careplan", ondelete="cascade", index=True, help="Document associated to"
    )
