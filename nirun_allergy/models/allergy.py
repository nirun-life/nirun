#  Copyright (c) 2021 NSTDA
from odoo import api, fields, models


class AllergyIntolerance(models.Model):
    _name = "ni.allergy"
    _description = "Allergy / Intolerance"
    _inherit = ["ni.patient.res"]

    type = fields.Selection(
        [("allergy", "Allergy"), ("intolerance", "Intolerance")],
        required=False,
        help="""
        Underlying mechanism, [Allergy] - A propensity for hypersensitive
        reaction(s) to a substance, [Intolerance] - not judged to be allergic or
         `allergy-like`. These reactions are typically (but not necessarily)
         non-immune.""",
    )
    code_id = fields.Reference(
        [
            ("ni.medication", "Medication"),
            ("ni.allergy.code", "Food / Environment / Biologic"),
        ],
        required=True,
        string="Substance",
    )
    category = fields.Selection(
        [
            ("food", "Food"),
            ("environment", "Environment"),
            ("biologic", "Biologic"),
            ("medication", "Medication"),
        ],
        compute="_compute_category",
        required=False,
    )
    criticality = fields.Selection(
        [("low", "Low"), ("high", "High"), ("unable-to-assess", "Unable to Access")],
        required=False,
    )
    state = fields.Selection(
        [("active", "Suffering"), ("inactive", "Not Active"), ("resolved", "Resolved")],
        required=True,
        default="active",
    )
    note = fields.Text()
    asserter_id = fields.Many2one(
        "res.partner",
        help="Source of the information about the allergy",
        required=False,
    )
    asserter_is_patient = fields.Boolean(store=False)
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
        name = "{} - {}".format(allergy.patient_id.name, allergy.code_id.name)
        if self._context.get("show_criticality"):
            name = "{}[{}]".format(name, allergy.get_severity_label())
        if self._context.get("show_category") and allergy.severity:
            name = "{} : {}".format(allergy.patient_id._name_get(), name)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, allergy.get_state_label())
        return name

    @api.onchange("asserter_is_patient")
    def _onchange_self_assert(self):
        if self.asserter_is_patient:
            self.asserter_id = self.patient_id.partner_id

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
            groupby="allergy_id",
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
