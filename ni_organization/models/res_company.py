#  Copyright (c) 2023 NSTDA
from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"
    _description = "Organization"

    @api.model
    def get_default_type(self):
        return self.env["res.company.type"].search([], limit=1) or None

    name = fields.Char(string="Organization Name")
    identifier = fields.Char(related="partner_id.identifier", readonly=False)

    type_id = fields.Many2one(
        "res.company.type", required=True, index=True, default=get_default_type
    )
    capacity = fields.Integer()
    capacity_unit = fields.Selection(
        [("bed", "Beds"), ("pat", "Patients per Day")], default="bed"
    )
    display_capacity = fields.Char(
        "Capacity with Unit", compute="_compute_display_capacity"
    )

    @api.depends("capacity", "capacity_unit")
    def _compute_display_capacity(self):
        units = dict(self._fields["capacity_unit"]._description_selection(self.env))
        for rec in self:
            if rec.capacity:
                rec.display_capacity = "{} {}".format(
                    rec.capacity, units.get(rec.capacity_unit, "")
                ).strip()
            else:
                rec.display_capacity = None

    @api.depends("name", "identifier")
    @api.depends_context("no_identifier")
    def _compute_display_name(self):
        for org in self:
            name = org.name
            if not self.env.context.get("no_identifier") and org.identifier:
                name = f"{name} ({org.identifier})"
            org.display_name = name

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        # Match every word of a multi-word name, or a single word on the name or
        # the identifier. The criterion goes into the domain, so the core
        # override still applies (user_preference company filter).
        domain = list(domain or [])
        if name and isinstance(name, str):
            words = name.split()
            if len(words) > 1:
                domain += [("name", operator, word) for word in words]
            else:
                domain += [
                    "|",
                    ("name", operator, name),
                    ("identifier", operator, name),
                ]
            name, operator = "", "ilike"
        return super()._name_search(name, domain, operator, limit, order)
