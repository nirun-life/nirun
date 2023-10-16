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
    display_capacity = fields.Char("Capacity", compute="_compute_display_capacity")

    @api.depends("capacity")
    def _compute_display_capacity(self):
        for rec in self:
            if rec.capacity:
                rec.display_capacity = "{} {}".format(
                    rec.capacity,
                    dict(self._field["capacity_unit"].selection(self))[
                        rec.capacity_unit
                    ],
                )
            else:
                rec.display_capacity = None

    def name_get(self):
        return [(org.id, org._get_name()) for org in self]

    def _get_name(self):
        org = self
        name = org.name
        if not self._context.get("no_identifier") and self.identifier:
            name = "{} ({})".format(name, self.identifier)
        return name

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
                    ("name", operator, name),
                    ("identifier", operator, name),
                ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
