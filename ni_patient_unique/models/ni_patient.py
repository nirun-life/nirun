#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    identification_id = fields.Char(store=True)

    _identification_id__uniq = models.Constraint(
        "unique (company_id, nationality_id, identification_id)",
        "Patient's identification ID must be unique!",
    )
