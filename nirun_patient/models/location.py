#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models


class Location(models.Model):
    _name = "ni.location"
    _description = "Location"
    _check_company_auto = True
    _order = "parent_path"
    _parent_store = True

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    name = fields.Char("Location Name", require=True, copy=False, index=True)
    alias = fields.Char("Alias Name", index=True)
    physical_type_id = fields.Many2one("ni.location.type", "Type", index=True)
    physical_type_name = fields.Char(
        related="physical_type_id.name", readonly=True, string="Type name"
    )
    parent_id = fields.Many2one("ni.location", string="Parent Location", index=True)
    parent_name = fields.Char(
        related="parent_id.name", readonly=True, string="Parent Location Name"
    )
    parent_path = fields.Char(index=True, readonly=True)
    child_ids = fields.One2many(
        "ni.location",
        "parent_id",
        string="Locations Inside",
        domain=[("active", "=", True)],
    )
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        (
            "company_id__parent_id__name__uniq",
            "unique (company_id, parent_id, name)",
            "Name is this location already exists !",
        ),
    ]

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(
                _("Error! You cannot create recursive locations.")
            )

    def name_get(self):
        if self._context.get("location_display") == "short":
            return super(Location, self).name_get()

        res = []
        for location in self:
            names = []
            current = location
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((location.id, ", ".join(reversed(names))))
        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(" / ")[-1]
            args = [("name", operator, name)] + args
        location_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(location_ids).with_user(name_get_uid))


class LocationType(models.Model):
    _name = "ni.location.type"
    _description = "Location Types"
    _inherit = ["coding.base"]
