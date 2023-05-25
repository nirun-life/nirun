#  Copyright (c) 2021-2023 NSTDA


from odoo import api, fields, models


class CodingSystem(models.Model):
    _name = "ni.coding.system"
    _description = "Coding System"
    _order = "sequence, id"

    def _get_default_sequence(self):
        other = self.env.ref("ni_coding.system_other")
        domain = [("id", "!=", other.id)] if other else []
        last_sequence = self.env[self._name].search(
            domain, order="sequence desc", limit=1
        )
        return last_sequence.sequence + 1 if last_sequence else 0

    sequence = fields.Integer(
        index=True,
        default=lambda self: self._get_default_sequence(),
    )
    name = fields.Char(required=True, index=True, translate=True)
    url = fields.Char()
    active = fields.Boolean(default=True)

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += ["|", ("name", operator, name), ("url", operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    _sql_constraints = [
        (
            "name__uniq",
            "unique (name)",
            "This name already exists!",
        ),
        (
            "url__uniq",
            "unique (url)",
            "This url already exists!",
        ),
    ]
