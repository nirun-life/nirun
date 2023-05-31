#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models


class ProcedureCode(models.Model):
    _inherit = "ni.procedure.code"

    code_simplify = fields.Char(
        compute="_compute_code_simplify", store=True, index=True
    )
    chapter_id = fields.Many2one("ni.procedure.chapter")

    _sql_constraints = [
        (
            "system_code_uniq",
            "unique (system_id, code, name)",
            "This code-name already exists!",
        ),
    ]

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += [
                "|",
                "|",
                ("name", operator, name),
                ("code", operator, name),
                ("code_simplify", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    @api.depends("code")
    def _compute_code_simplify(self):
        for rec in self:
            if rec.code:
                rec.code_simplify = rec.code.replace(".", "")
