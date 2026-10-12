#  Copyright (c) 2021-2023 NSTDA
import random
from pathlib import Path

from lxml import etree

from odoo import api, fields, models
from odoo.osv import expression


class Coding(models.AbstractModel):
    _name = "ni.coding"
    _description = "Coding"
    _order = "sequence, id"
    _rec_names_search = ["name", "code", "abbr"]

    _display_name_separator = ", "
    _default_coding_form = (
        Path(__file__).parent.parent / "views" / "ni_coding_default_form.xml"
    )
    _default_coding_list = (
        Path(__file__).parent.parent / "views" / "ni_coding_default_list.xml"
    )
    _default_coding_search = (
        Path(__file__).parent.parent / "views" / "ni_coding_default_search.xml"
    )
    _default_coding_kanban = (
        Path(__file__).parent.parent / "views" / "ni_coding_default_kanban.xml"
    )

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        can_write = self.has_access("write")
        use_default = not view or (view_type == "form" and not can_write)
        if use_default:
            default_path = getattr(self, f"_default_coding_{view_type}", None)
            if default_path:
                arch = etree.parse(str(default_path)).getroot()
        return arch, view

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
    def _search_display_name(self, operator, value):
        # A multi-word query must match every word of the name.
        if operator in ("ilike", "like") and isinstance(value, str):
            words = value.split()
            if len(words) > 1:
                return expression.AND([[("name", operator, word)] for word in words])
        return super()._search_display_name(operator, value)

    @api.depends(
        lambda self: ["name", "abbr", "code"]
        + (["parent_id.name"] if "parent_id" in self._fields else [])
    )
    @api.depends_context("show_parent", "show_abbr", "show_code", "only_abbr")
    def _compute_display_name(self):
        for coding in self:
            coding.display_name = coding._get_name()

    def _get_name(self):
        coding = self
        name = coding.name
        context = self.env.context
        if (
            context.get("show_parent")
            and "parent_id" in self._fields
            and coding._fields["parent_id"]
        ):
            names = []
            current = coding
            while current:
                names.append(current.name)
                current = current.parent_id
            name = self._display_name_separator.join(reversed(names))
        if context.get("show_abbr") and self.abbr:
            name = f"{name} ({coding.abbr})"
        if context.get("show_code") and self.code:
            name = f"[{coding.code}] {name}"
        if context.get("only_abbr") and self.abbr:
            name = coding.abbr
        return name

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        for coding, vals in zip(self, vals_list, strict=True):
            if "name" not in default:
                vals["name"] = f"{coding.name} (copy)"
            if "code" not in default and coding.code:
                vals["code"] = f"{coding.code} (copy)"
        return vals_list
