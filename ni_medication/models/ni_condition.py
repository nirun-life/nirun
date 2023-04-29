#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class Condition(models.Model):
    _inherit = "ni.condition"

    medication_statement_ids = fields.Many2many(
        "ni.medication.statement",
        "ni_medication_statement_condition",
        "condition_id",
        "statement_id",
        "Medication Statement",
        readonly=True,
    )
