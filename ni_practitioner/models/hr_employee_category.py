#  Copyright (c) 2023 NSTDA
from odoo import api, fields, models


class EmployeeCategory(models.Model):
    """
    Use hr.employee.category as Practitioner.Role.Code
    """

    _name = "hr.employee.category"
    _inherit = ["hr.employee.category", "ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("hr.employee.category", index=True, ondelete="cascade")
    parent_path = fields.Char(index=True)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise models.ValidationError(
                self.env._("Error! You cannot create recursive data.")
            )
