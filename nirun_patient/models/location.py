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

    encounter_ids = fields.One2many("ni.encounter", "location_id")
    patient_ids = fields.One2many(
        "ni.patient", compute="_compute_patient_count", compute_sudo=True
    )
    patient_count = fields.Integer(
        "Total", compute="_compute_patient_count", store=True, compute_sudo=True
    )
    patient_male_count = fields.Integer(
        "Male", compute="_compute_patient_count", store=True, compute_sudo=True
    )
    patient_female_count = fields.Integer(
        "Female", compute="_compute_patient_count", store=True, compute_sudo=True
    )

    _sql_constraints = [
        (
            "company_id__parent_id__name__uniq",
            "unique (company_id, parent_id, name)",
            "Name is this location already exists !",
        ),
    ]

    @api.depends("encounter_ids")
    def _compute_patient_count(self):
        for rec in self:
            rec.patient_ids = rec.encounter_ids.mapped("patient_id")
            rec.patient_count = len(rec.patient_ids)
            rec.patient_male_count = len(
                rec.patient_ids.filtered(lambda p: p.gender == "male")
            )
            rec.patient_female_count = len(
                rec.patient_ids.filtered(lambda p: p.gender == "female")
            )

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

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
            args = ["|", ("name", operator, name), ("alias", operator, name)] + args
        location_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(location_ids).with_user(name_get_uid))
