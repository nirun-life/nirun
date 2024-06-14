#  Copyright (c) 2021-2023 NSTDA
import random

from odoo import api, fields, models


class Coding(models.AbstractModel):
    _name = "ni.coding"
    _description = "Coding"
    _order = "sequence, id"

    _display_name_separator = ", "

    def _get_default_sequence(self):
        last_sequence = self.env[self._name].search([], order="sequence desc", limit=1)
        return last_sequence.sequence + 1 if last_sequence else 0

    sequence = fields.Integer(
        index=True,
        default=lambda self: self._get_default_sequence(),
    )
    name = fields.Char(required=True, index="trigram", translate=True)
    abbr = fields.Char("Abbreviation", index="btree_not_null")
    code = fields.Char(index=True, size=16)
    system_id = fields.Many2one(
        "ni.coding.system",
        index=True,
        default=lambda self: self.env.ref("ni_coding.system_internal"),
    )
    system = fields.Char(related="system_id.url")
    definition = fields.Text(translate=True)
    color = fields.Integer(default=lambda _: random.randint(0, 10))
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "system_name_uniq",
            "unique (system_id, name)",
            "This name already exists!",
        ),
        (
            "system_code_uniq",
            "unique (system_id, code)",
            "This code already exists!",
        ),
    ]

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            if len(name.split()) > 1:
                for n in name.split():
                    args.append(("name", operator, n))
            else:
                args += [
                    "|",
                    "|",
                    ("name", operator, name),
                    ("code", operator, name),
                    ("abbr", operator, name),
                ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        return [(code.id, code._get_name()) for code in self]

    def _get_name(self):
        coding = self
        name = coding.name
        if (
            self._context.get("show_parent")
            and "parent_id" in self._fields
            and coding._fields["parent_id"]
        ):
            names = []
            current = coding
            while current:
                names.append(current.name)
                current = current.parent_id
            name = self._display_name_separator.join(reversed(names))
        if self._context.get("show_abbr") and self.abbr:
            name = "{} ({})".format(name, coding.abbr)
        if self._context.get("show_code") and self.code:
            name = "[{}] {}".format(coding.code, name)
        if self._context.get("only_abbr") and self.abbr:
            name = coding.abbr
        return name

    def copy(self, default=None):
        default = default or {}
        if "name" not in default:
            default["name"] = "%s (copy)" % self.name
        if "code" not in default and self.code:
            default["code"] = "%s (copy)" % self.code
        return super(Coding, self).copy(default)
