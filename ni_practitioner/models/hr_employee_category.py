#  Copyright (c) 2023 NSTDA
from odoo import _, api, fields, models


class EmployeeCategory(models.Model):
    """
    Use hr.employee.category as Practitioner.Role.Code
    """

    _name = "hr.employee.category"
    _inherit = ["hr.employee.category", "ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("hr.employee.category", index=True, ondelete="cascade")
    parent_path = fields.Char(index=True, unaccent=False)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive item."))
