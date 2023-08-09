#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models


class CopayType(models.Model):
    _name = "ni.coverage.type"
    _description = "Coverage Type"
    _inherit = ["ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("ni.coverage.type", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    kind = fields.Selection(
        [("insurance", "Insurance"), ("self-pay", "Self-Pay"), ("other", "Other")],
        default="insurance",
        required=True,
    )

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
