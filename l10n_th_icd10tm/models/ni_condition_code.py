#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class ConditionCode(models.Model):
    _inherit = "ni.condition.code"

    code_simplify = fields.Char(
        compute="_compute_code_simplify", store=True, index=True
    )
    chapter_id = fields.Many2one(
        "ni.condition.chapter", related="block_id.chapter_id", store=True
    )
    block_id = fields.Many2one("ni.condition.block")
    level = fields.Integer(default=1)
    type = fields.Selection(
        [("code", "Code"), ("header", "Header")], default="code", required=True
    )

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            if name.split():
                for n in name.split():
                    args.append(("name", operator, n))
            else:
                args += [
                    "|" "|",
                    "|",
                    ("name", operator, name),
                    ("code", operator, name),
                    ("code_simplify", operator, name),
                    ("abbr", operator, name),
                ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    @api.depends("code")
    def _compute_code_simplify(self):
        for rec in self:
            if rec.code:
                rec.code_simplify = rec.code.replace(".", "")
