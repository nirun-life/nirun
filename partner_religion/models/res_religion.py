#  Copyright (c) 2021-2023 NSTDA
import random

from odoo import _, api, fields, models


class Religion(models.Model):
    _name = "res.religion"
    _description = "Religions"
    _parent_store = True
    _order = "sequence"

    _display_name_separator = ", "

    def _get_default_sequence(self):
        last_sequence = self.env[self._name].search([], order="sequence desc", limit=1)
        return last_sequence.sequence + 1 if last_sequence else 0

    sequence = fields.Integer(
        index=True,
        default=lambda self: self._get_default_sequence(),
    )

    name = fields.Char(
        string="Religion Name",
        required=True,
        translate=True,
        help="The full name of the Religion.",
    )
    abbr = fields.Char("Abbreviation", index="btree_not_null")
    parent_id = fields.Many2one("res.religion", string="Major", index=True)
    parent_path = fields.Char(
        index=True,
        unaccent=False,
        readonly=True,
        groups="base.group_partner_manager",
    )
    child_ids = fields.One2many(
        "res.religion", "parent_id", string="Denominations", readonly=True
    )
    color = fields.Integer(default=lambda _: random.randint(0, 10))
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ("name_uniq", "unique (name)", _("Name of the religion must be unique !"))
    ]

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        domain = list(domain or [])
        if not (name == "" and operator == "ilike"):
            if len(name.split()) > 1:
                for n in name.split():
                    domain.append(("name", operator, n))
            else:
                domain += [
                    "|",
                    ("name", operator, name),
                    ("abbr", operator, name),
                ]
        return self._search(domain, limit=limit, order=order)

    @api.depends("name", "abbr", "parent_id.name")
    @api.depends_context("show_parent", "show_abbr", "only_abbr")
    def _compute_display_name(self):
        for religion in self:
            religion.display_name = religion._get_name()

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
        if context.get("only_abbr") and self.abbr:
            name = coding.abbr
        return name

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
