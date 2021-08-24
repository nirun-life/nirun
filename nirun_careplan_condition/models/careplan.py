#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Careplan(models.Model):
    _inherit = "ni.careplan"

    condition_ids = fields.Many2many(
        "ni.condition",
        "ni_careplan_condition_rel",
        "careplan_id",
        "condition_id",
        store=True,
        readonly=False,
        check_company=True,
        compute="_compute_condition",
    )

    @api.depends("condition_ids", "activity_ids.reason_condition_ids")
    def _compute_condition(self):
        for plan in self:
            c1 = plan.mapped("activity_ids.reason_condition_ids.id")
            c2 = plan.mapped("condition_ids.id")
            plan.condition_ids = list(set().union(c1, c2))
