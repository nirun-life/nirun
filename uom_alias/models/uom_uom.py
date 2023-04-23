#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class UoM(models.Model):
    _inherit = "uom.uom"

    alias = fields.Char()

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += ["|", ("name", operator, name), ("alias", operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
