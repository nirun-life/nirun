#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class FlagConflictWizard(models.TransientModel):
    _name = "ni.flag.conflict.wizard"
    _description = "Flag Conflict Wizard"

    recommendation_id = fields.Many2one(
        "ni.flag.recommendation",
        required=True,
        default=lambda self: self.env.context.get("default_recommendation_id"),
    )
    conflict_flag_ids = fields.Many2many(
        "ni.flag",
        compute="_compute_conflict_flag_ids",
        string="Conflicting Flags",
    )

    def _compute_conflict_flag_ids(self):
        for rec in self:
            rec.conflict_flag_ids = rec.recommendation_id._conflicting_active_flags()

    def action_confirm(self):
        self.ensure_one()
        self.recommendation_id.with_context(
            force_conflict_resolution=True
        ).action_accept()
        return {"type": "ir.actions.act_window_close"}
