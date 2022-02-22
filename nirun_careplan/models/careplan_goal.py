#  Copyright (c) 2022 Piruin P.

from odoo import api, fields, models


class CareplanGoal(models.Model):
    _name = "ni.careplan.goal"
    _description = "Careplan Goal"
    _inherit = ["ni.goal", "mail.thread", "mail.activity.mixin"]
    _order = "sequence"

    careplan_id = fields.Many2one(
        "ni.careplan", required=True, index=True, ondelete="cascade", copy=False
    )
    patient_id = fields.Many2one(
        "ni.patient", related="careplan_id.patient_id", copy=False, store=True
    )
    encounter_id = fields.Many2one(
        "ni.encounter", related="careplan_id.encounter_id", copy=False
    )
    company_id = fields.Many2one(
        "res.company", related="careplan_id.company_id", copy=False, store=True,
    )
    condition_id = fields.Many2one("ni.condition", index=True, ondelete="set null")
    _sql_constraints = [
        ("code__uniq", "unique (careplan_id, code_id)", "Goal must be unqiue!"),
    ]

    @api.model
    def _group_expand_state(self, states, domain, order):
        return [key for key, val in type(self).state.selection]
