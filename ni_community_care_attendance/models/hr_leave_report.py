from odoo import models


class LeaveReport(models.Model):
    _inherit = "hr.leave.report"

    def action_time_off_analysis(self):
        action = super().action_time_off_analysis()
        ctx = dict(action.get("context", {}) or {})
        ctx["search_default_my_area_employees"] = 1
        action["context"] = ctx
        return action
