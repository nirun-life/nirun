#  Copyright (c) 2021-2023 NSTDA


from odoo import fields, models


class CodingSystem(models.Model):
    _name = "ni.coding.system"
    _description = "Coding System"
    _order = "sequence, id"
    _rec_names_search = ["name", "url"]

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
    name = fields.Char(required=True, index="trigram", translate=True)
    url = fields.Char()
    active = fields.Boolean(default=True)

    _name__uniq = models.Constraint(
        "unique (name)",
        "This name already exists!",
    )
    _url__uniq = models.Constraint(
        "unique (url)",
        "This url already exists!",
    )
