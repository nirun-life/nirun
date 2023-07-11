#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class Location(models.Model):
    _name = "ni.location"
    _description = "Location"
    _check_company_auto = True
    _order = "display_name"
    _parent_store = True

    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    name = fields.Char("Location Name", required=True, copy=False, index=True)
    display_name = fields.Char(compute="_compute_display_name", store=True, index=True)
    alias = fields.Char("Alias Name", index=True)
    physical_type_id = fields.Many2one("ni.location.type", "Type", index=True)
    physical_type_name = fields.Char(
        related="physical_type_id.name", readonly=True, string="Type name"
    )
    parent_id = fields.Many2one("ni.location", string="Parent Location", index=True)
    parent_name = fields.Char(
        related="parent_id.name", readonly=True, string="Parent Location Name"
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(
        "ni.location",
        "parent_id",
        string="Locations Inside",
        domain=[("active", "=", True)],
    )
    child_count = fields.Integer(compute="_compute_child_count", store=True)
    active = fields.Boolean("Active", default=True)

    encounter_ids = fields.One2many("ni.encounter", "location_id")
    encounter_active_ids = fields.One2many(
        "ni.encounter",
        "location_id",
        string="Encounter",
        compute="_compute_patient_count",
        compute_sudo=True,
    )
    encounter_active_count = fields.Integer(
        compute="_compute_patient_count", string="Encounter", compute_sudo=True
    )
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

    @api.depends("child_ids", "child_ids.parent_path")
    def _compute_child_count(self):
        for rec in self:
            rec.child_count = rec._get_child_count()

    def _get_child_count(self):
        self.ensure_one()
        count = 0
        for child in self.child_ids:
            count += child._get_child_count()
        count += len(self.child_ids)
        return count

    @api.depends("encounter_ids", "encounter_ids.state")
    def _compute_patient_count(self):
        for rec in self:
            rec.encounter_active_ids = rec._get_encounter_active_ids()
            rec.encounter_active_count = len(rec.encounter_active_ids)
            rec.patient_ids = rec.encounter_active_ids.mapped("patient_id")
            rec.patient_count = len(rec.patient_ids)
            rec.patient_male_count = len(
                rec.patient_ids.filtered(lambda p: p.gender == "male")
            )
            rec.patient_female_count = len(
                rec.patient_ids.filtered(lambda p: p.gender == "female")
            )

    def _get_encounter_active_ids(self):
        self.ensure_one()
        enc_ids = []
        for child in self.child_ids:
            enc_ids += child._get_encounter_active_ids()
        enc_ids += self.encounter_ids.filtered_domain(
            [("state", "=", "in-progress")]
        ).ids
        return enc_ids

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

    @api.depends("parent_name", "parent_id", "name")
    def _compute_display_name(self):
        diff = dict(location_display=None, show_alias=True)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    def name_get(self):
        res = []
        for rec in self:
            name = rec._get_name()
            res.append((rec.id, name))
        return res

    def _get_name(self):
        self.ensure_one()
        if self._context.get("location_display") == "short":
            return self.name

        names = []
        current = self
        while current:
            names.append(current.name)
            current = current.parent_id
        name = ", ".join(reversed(names))
        if self._context.get("show_alias", True) and self.alias:
            name = "{} ({})".format(name, self.alias)
        return name

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if name:
            args = [
                "|",
                ("display_name", operator, name),
                ("alias", operator, name),
            ] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
