#  Copyright (c) 2021 Piruin P.

import random

from odoo import fields, models


class CodingBase(models.AbstractModel):
    _name = "coding.base"
    _description = "Coding"
    _order = "sequence, id"

    sequence = fields.Integer(index=True, default=0,)
    name = fields.Char(required=True, index=True, translate=True, copy=False)
    code = fields.Char(index=True, copy=False, limit=16)
    definition = fields.Text(translate=True)
    color = fields.Integer(default=lambda _: random.randint(0, 10))
    active = fields.Boolean(default=True)

    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += ["|", ("name", operator, name), ("code", operator, name)]
        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(ids).with_user(name_get_uid))

    def name_get(self):
        if self.env.context.get("show_code"):
            return [
                (
                    codeable.id,
                    "[{}] {}".format(codeable.code, codeable.name)
                    if codeable.code
                    else codeable.name,
                )
                for codeable in self
            ]
        return super(CodingBase, self).name_get()

    _sql_constraints = [
        ("name__uniq", "unique (name)", "This name already exists!",),
        ("code__uniq", "unique (code)", "This code already exists!",),
    ]
