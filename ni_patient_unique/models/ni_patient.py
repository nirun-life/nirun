#  Copyright (c) 2025 NSTDA
from odoo import _, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    identification_id = fields.Char(store=True)

    _sql_constraints = [
        (
            "identification_id__uniq",
            "unique (company_id, nationality_id, identification_id)",
            _("Patient's identification ID must be unique!"),
        ),
    ]
