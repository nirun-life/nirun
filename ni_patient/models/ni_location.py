#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models
from odoo.osv import expression


class Location(models.Model):
    _name = "ni.location"
    _description = "Location"
    _check_company_auto = True
    _order = "parent_path"
    _parent_store = True

    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    name = fields.Char("Location Name", required=True, copy=False, index=True)
    # We not use display name to show full path name cause it affect on search panel
    full_name = fields.Char("Location", compute="_compute_full_name")
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
    def _compute_full_name(self):
        diff = dict(location_display=None, show_alias=True, show_parent=True)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.full_name = names.get(rec.id)

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

        if self._context.get("show_parent"):
            names = []
            current = self
            while current:
                names.append(current.name)
                current = current.parent_id
            name = ", ".join(reversed(names))
        else:
            name = self.name
        if self._context.get("show_alias", True) and self.alias:
            name = "{} ({})".format(name, self.alias)
        return name

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if name:
            # display_name matched every location instead of none: it is neither stored nor given
            # a search method, so the ORM logs "Non-stored field ... cannot be searched" and turns
            # the leaf into TRUE - any name typed into a location autocomplete, or any
            # ('<m2o to a location>', 'ilike', ...) leaf, returned the whole table.
            # _rec_names_search is what name_get is composed from anyway, and reading it here means
            # models extending this one are searched on their own fields too (ni.location.commu
            # adds "code").
            names = list(self._rec_names_search or [self._rec_name]) + ["alias"]
            # A negated leaf has to be joined with AND, or "not ilike" matches on one field what
            # the other excludes and the whole table comes back again - expression.py hands us
            # the raw operator for a m2o leaf, negatives included.
            aggregator = (
                expression.AND
                if operator in expression.NEGATIVE_TERM_OPERATORS
                else expression.OR
            )
            args = aggregator([[(field, operator, name)] for field in names]) + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
