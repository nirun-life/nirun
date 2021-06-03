#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Condition(models.Model):
    _inherit = "ni.condition"

    medication_statement_ids = fields.Many2many(
        "ni.medication.statement",
        "ni_medication_statement_condition_rel",
        "condition_id",
        "statement_id",
        "Medication Statements",
        readonly=True,
    )
