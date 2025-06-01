#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class CareplanCategory(models.Model):
    _name = "ni.careplan.category"
    _description = "Careplan Category"
    _inherit = ["ni.coding"]

    _parent_store = True

    parent_id = fields.Many2one("ni.careplan.category", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    goal_category_id = fields.Many2one("ni.goal.category", help="Default goal category")
    service_category_id = fields.Many2one(
        "ni.service.category", help="Default service category"
    )

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
