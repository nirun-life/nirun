#  Copyright (c) 2021-2023 NSTDA
from odoo import api, fields, models


class MedicationSuggestion(models.Model):
    _name = "ni.medication.suggest"
    _description = "Medication Suggestion"
    _inherit = ["ni.coding"]

    user_id = fields.Many2one(
        "res.users", required=False, help="this suggestion belong to user"
    )
    line_ids = fields.One2many("ni.medication.suggest.line", "suggest_id", "Medication")
    line_count = fields.Integer(compute="_compute_line_display", store=True)
    line_display = fields.Char(
        "Medication", compute="_compute_line_display", store=True
    )
    reason_ids = fields.Many2many("ni.encounter.reason")

    @api.depends("line_ids")
    def _compute_line_display(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)
            if rec.line_ids:
                rec.line_display = ", ".join([line.name for line in rec.line_ids])
            else:
                rec.line_display = False


class MedicationSuggestionLine(models.Model):
    _name = "ni.medication.suggest.line"
    _description = "Medication Suggestion Line"
    _inherit = ["ni.medication.abstract"]

    name = fields.Char(related="medication_id.name")

    suggest_id = fields.Many2one("ni.medication.suggest")

    category_id = fields.Many2one(
        "ni.medication.admin.location", required=False, copy=False
    )
    quantity = fields.Float(required=True)
    reason_id = fields.Many2one(
        "ni.encounter.reason", domain="[('id', 'in', reason_ids)]"
    )
    reason_ids = fields.Many2many(related="suggest_id.reason_ids")
