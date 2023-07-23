# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    license_id = fields.Many2one("hr.resume.line")
