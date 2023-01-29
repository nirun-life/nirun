#  Copyright (c) 2023. NSTDA
from odoo import api, fields, models


class Careplan(models.Model):
    _inherit = "ni.careplan"

    employee_ids = fields.Many2many(
        "hr.employee", compute="_compute_employee_ids", readonly=True
    )

    @api.depends("goal_ids.employee_id")
    def _compute_employee_ids(self):
        for rec in self:
            rec.employee_ids = rec.goal_ids.mapped("employee_id")


class Goal(models.Model):
    _inherit = "ni.goal"

    employee_id = fields.Many2one("hr.employee")


class CareplanActivity(models.Model):
    _inherit = "ni.careplan.activity"

    # Set require to false for making it possible to save activity form that
    # started by One2Many Tree widget of careplan
    careplan_id = fields.Many2one(required=False)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        related=False,
        readonly=False,
    )
