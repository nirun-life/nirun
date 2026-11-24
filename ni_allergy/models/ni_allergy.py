#  Copyright (c) 2021-2023 NSTDA
from odoo import api, fields, models


class AllergyIntolerance(models.Model):
    _name = "ni.allergy"
    _description = "Allergy / Intolerance"
    _inherit = ["ni.patient.res"]
    _order = "sequence, name"

    sequence = fields.Integer(default=0)
    name = fields.Char("Allergy Name", required=True)
    code_id = fields.Many2one(
        "ni.allergy.code",
        required=False,
        string="Substance",
    )
    code = fields.Char(related="code_id.code", store=True)
    category = fields.Selection(
        [
            ("food", "Food"),
            ("environment", "Environment"),
            ("biologic", "Biologic"),
            ("medication", "Medication"),
        ],
        default="food",
        required=True,
        index=True,
    )
    type = fields.Selection(
        [("allergy", "Allergy"), ("intolerance", "Intolerance")],
        default="allergy",
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
    reaction_count = fields.Integer(compute="_compute_reaction_count")
    last_occurrence = fields.Datetime(compute="_compute_last_occurrence", store=True)

    _patient_allergy__uniq = models.Constraint(
        "unique (patient_id, code_id)",
        "Patient already have this allergy recorded!",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if "name" not in val and "code_id" in val:
                code = self.env["ni.allergy.code"].browse(val["code_id"])
                val["name"] = code.name
        return super().create(vals_list)

    @api.onchange("code_id")
    def _onchange_code_id(self):
        for rec in self.filtered(lambda r: r.code_id):
            rec.name = rec.code_id.name

    @api.depends(
        "name", "code_id.name", "criticality", "state", "patient_id.display_name"
    )
    @api.depends_context(
        "show_patient",
        "show_criticality",
        "show_state",
        # of the patient name
        "show_identifier",
        "show_identification_id",
        "show_gender_age",
        "show_age",
    )
    def _compute_display_name(self):
        for allergy in self:
            allergy.display_name = allergy._name_get()

    def _name_get(self):
        allergy = self
        name = allergy.code_id.name or allergy.name
        if self.env.context.get("show_patient"):
            name = f"{allergy.patient_id._name_get()} - {name}"
        if self.env.context.get("show_criticality") and allergy.criticality:
            name = f"{name}[{allergy._get_criticality_label()}]"
        if self.env.context.get("show_state"):
            name = f"{name} ({allergy._get_state_label()})"
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

    @api.depends("reaction_ids")
    def _compute_reaction_count(self):
        for rec in self:
            rec.reaction_count = len(rec.reaction_ids)

    @api.depends("reaction_ids.onset")
    def _compute_last_occurrence(self):
        reactions = self.env["ni.allergy.reaction"]._read_group(
            [("allergy_id", "in", self.ids)], ["allergy_id"], ["onset:max"]
        )
        result = {allergy.id: onset for allergy, onset in reactions}
        for allergy in self:
            allergy.last_occurrence = result.get(allergy.id)

    def action_inactive(self):
        self.write({"state": "inactive"})

    def action_active(self):
        self.write({"state": "active"})

    def action_resolve(self):
        self.write({"state": "resolved", "sequence": 99})

    def _get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    def _get_criticality_label(self):
        self.ensure_one()
        return dict(self._fields["criticality"].selection).get(self.criticality)
