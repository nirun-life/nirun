#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class HrJob(models.Model):
    _inherit = "hr.job"

    document_ref_type_id = fields.Many2one(
        "ni.document.ref.type", help="default document ref type for this job role"
    )
