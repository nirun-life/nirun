from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    motto = fields.Text(help="Employee's Motto...")
