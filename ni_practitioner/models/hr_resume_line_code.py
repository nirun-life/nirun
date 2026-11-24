#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models


class ResumeLineCode(models.Model):
    _name = "hr.resume.line.code"
    _description = "Code of a resume line"
    _inherit = "ni.coding"
    _parent_store = True

    parent_id = fields.Many2one("hr.resume.line.code", index=True, ondelete="set null")
    parent_path = fields.Char(index=True)

    issuer_id = fields.Many2one("res.partner", domain="[('is_company', '=', True)]")
    type_id = fields.Many2one("hr.resume.line.type")
    require_identifier = fields.Boolean(default=False)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise models.ValidationError(
                self.env._("Error! You cannot create recursive data.")
            )
