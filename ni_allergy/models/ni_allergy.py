#  Copyright (c) 2021-2023 NSTDA
from odoo import api, fields, models


class AllergyIntolerance(models.Model):
    _name = "ni.allergy"
    _description = "Allergy / Intolerance"
    _inherit = ["ni.patient.res"]
    _rec_name = "code_id"

    code_id = fields.Many2one(
        "ni.allergy.code",
        required=True,
        string="Substance",
    )
    category = fields.Selection(
        related="code_id.category",
        store=True,
    )
    type = fields.Selection(
        [("allergy", "Allergy"), ("intolerance", "Intolerance")],
        required=False,
        help="""
        Underlying mechanism, [Allergy] - A propensity for hypersensitive
        reaction(s) to a substance, [Intolerance] - not judged to be allergic or
         `allergy-like`. These reactions are typically (but not necessarily)
         non-immune.""",
    )
    criticality = fields.Selection(
        [("low", "Low"), ("high", "High"), ("unable-to-assess", "Unable to Access")],
        required=False,
    )
    state = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive"), ("resolved", "Resolved")],
        required=True,
        default="active",
    )
    note = fields.Text()

    reaction_ids = fields.One2many("ni.allergy.reaction", "allergy_id", "Reaction")
    last_occurrence = fields.Datetime(compute="_compute_last_occurrence", store=True)

    _sql_constraints = [
        (
            "patient_allergy__uniq",
            "unique (patient_id, code_id)",
            "Patient already have this allergy recorded!",
        ),
    ]

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        allergy = self
        name = allergy.code_id.name
        if self._context.get("show_patient"):
            name = "{} - {}".format(allergy.patient_id._name_get(), name)
        if self._context.get("show_criticality"):
            name = "{}[{}]".format(name, allergy._get_criticality_label())
        if self._context.get("show_state"):
            name = "{} ({})".format(name, allergy._get_state_label())
        return name

    @api.depends("code_id")
    def _compute_category(self):

        for rec in self:
            rec.category = None
            if not rec.code_id:
                continue
            ref = str(rec.code_id)
            if ref.startswith("ni.allergy.code"):
                rec.category = rec.code_id.category
            if ref.startswith("ni.medication"):
                rec.category = "medication"

    @api.depends("reaction_ids.onset")
    def _compute_last_occurrence(self):
        reactions = self.env["ni.allergy.reaction"].read_group(
            domain=[("allergy_id", "in", self.ids)],
            fields=["onset:max"],
            groupby=["allergy_id"],
            orderby="allergy_id",
        )
        import pprint

        pprint.pprint(reactions)
        result = {data["allergy_id"][0]: data["onset"] for data in reactions}
        for allergy in self:
            allergy.last_occurrence = result.get(allergy.id, 0)

    def action_inactive(self):
        self.write({"state": "inactive"})

    def action_active(self):
        self.write({"state": "active"})

    def action_resolve(self):
        self.write({"state": "resolved"})

    def _get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    def _get_criticality_label(self, vals):
        self.ensure_one()
        return dict(self._fields["criticality"].selection).get(self.criticality)
