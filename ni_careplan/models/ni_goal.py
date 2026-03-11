from odoo import fields, models


class Goal(models.Model):
    _inherit = "ni.goal"

    careplan_id = fields.Many2one(
        "ni.careplan", index=True, help="What goal fulfills", ondelete="cascade"
    )

    def _check_period_start_encounter(
        self, encounter_id, period_start, vals: dict = None
    ):
        # careplan may be created in advance or reversed way
        # so Ignore careplan.period_start and encounter.period_start check
        if vals.get("careplan_id") or getattr(self, "careplan_id", None):
            return
        return super()._check_period_start_encounter(encounter_id, period_start)
