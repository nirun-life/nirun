#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class BodySite(models.Model):
    _name = "ni.body.site"
    _description = "Body Site (Body Structure)"
    _inherit = "ni.coding"

    _parent_store = True

    parent_id = fields.Many2one("ni.body.site", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
