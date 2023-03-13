#  Copyright (c) 2022-2023. NSTDA
from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"
    _order = "period_start DESC,name DESC"

    priority = fields.Selection(groups="base.group_no_one")
    pre_admit_identifier = fields.Char(groups="base.group_no_one")
    period_end = fields.Date("Discharge Date")

    case_manager_id = fields.Many2one(
        "hr.employee",
    )
    case_manager_job_title = fields.Char(related="case_manager_id.job_title")

    def action_dummy(self):
        return {}
