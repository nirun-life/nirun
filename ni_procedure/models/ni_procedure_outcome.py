#  Copyright (c) 2022. NSTDA
from odoo import fields, models


class ProcedureOutcome(models.Model):
    _name = "ni.procedure.outcome"
    _description = "Procedure Outcome"
    _inherit = ["ni.coding"]

    display_class = fields.Selection(
        [
            ("text", "Text"),
            ("muted", "Muted"),
            ("info", "Info"),
            ("primary", "Primary"),
            ("success", "Success"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        default="text",
    )
