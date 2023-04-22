#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class MedicationStatement(models.Model):
    _inherit = "ni.medication.statement"

    reason_condition_ids = fields.Many2many(
        "ni.condition",
        "ni_medication_statement_condition_rel",
        "statement_id",
        "condition_id",
        "Conditions",
        help="Why medication is being/was taken",
    )
    reason_condition_id = fields.Many2one(
        "ni.condition",
        "Condition (Main)",
        help="Main reason of this medication statement",
    )
