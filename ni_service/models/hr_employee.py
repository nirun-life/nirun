#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    department_color = fields.Integer("Department Color", related="department_id.color")
