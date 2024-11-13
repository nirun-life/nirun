#  Copyright (c) 2021 NSTDA
from odoo import api, fields, models, tools
from odoo.tools.date_utils import get_timedelta


class Observation(models.Model):
    _name = "ni.observation"
    _description = "Observation"
    _inherit = ["ni.workflow.event.mixin", "ni.observation.abstract"]
    _order = "occurrence DESC,patient_id,sequence"

    @api.model
    def default_get(self, fields):
        res = super(Observation, self).default_get(fields)
        if "patient_id" in fields and "patient_id" not in res:
            if self.env.context.get("active_model") == "ni.observation.sheet":
                res["sheet_id"] = self.env.context["active_id"]
            if self.env.context.get("active_model") == "ni.encounter":
                res["encounter_id"] = self.env.context["active_id"]
            if self.env.context.get("active_model") == "ni.patient":
                res["patient_id"] = self.env.context["active_id"]
        return res

    sheet_id = fields.Many2one(
        "ni.observation.sheet",
        required=False,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    compare = fields.Selection(compute="_compute_compare")
    compare_interpret = fields.Selection(compute="_compute_compare")

    _sql_constraints = [
        (
            "type__uniq",
            "unique (sheet_id, type_id)",
            "Duplication observation type!",
        ),
    ]

    @api.depends("value_float", "value_int", "occurrence", "type_id", "type_id.compare")
    def _compute_compare(self):
        for rec in self:
            if rec.type_id.value_type not in ["int", "float"]:
                rec.compare = None
                continue

            prev = self.search(
                [
                    ("patient_id", "=", rec.patient_id.id),
                    ("type_id", "=", rec.type_id.id),
                    ("occurrence", "<", rec.occurrence),
                ],
                order="occurrence desc",
                limit=1,
            )
            if not prev:
                rec.compare = None
                continue

            # Get the value based on the type_id's value_type
            field_name = f"value_{rec.type_id.value_type}"
            current_value = getattr(rec, field_name)
            previous_value = getattr(prev, field_name)

            if current_value == previous_value:
                rec.compare = "eq"
                rec.compare_interpret = "neutral"
            elif current_value < previous_value:
                rec.compare = "lt"
                rec.compare_interpret = (
                    "better" if rec.type_id.compare == "low" else "worsen"
                )
            else:
                rec.compare = "gt"
                rec.compare_interpret = (
                    "better" if rec.type_id.compare == "high" else "worsen"
                )

    def init(self):
        tools.create_index(
            self._cr,
            "ni_observation__patient__ob_type__idx",
            self._table,
            ["patient_id", "type_id"],
        )
        tools.create_index(
            self._cr,
            "ni_observation__encounter__ob_type__idx",
            self._table,
            ["encounter_id", "type_id"],
        )

    @api.constrains("sheet_id", "occurrence")
    def _check_occurrence(self):
        # effective date must always depend on observation sheet
        for rec in self.filtered(lambda r: r.sheet_id):
            if rec.occurrence != rec.sheet_id.occurrence:
                rec.occurrence = rec.sheet_id.occurrence

    @api.constrains("sheet_id", "patient_id")
    def _check_sheet_patient(self):
        for rec in self.filtered(lambda r: r.sheet_id):
            if rec.patient_id != rec.sheet_id.patient_id:
                rec.patient_id = rec.sheet_id.patient_id

    def view_graph(self):
        action_rec = self.env.ref("ni_observation.ni_observation_action_graph").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.patient_id.id,
                "search_default_type_id": self.type_id.id,
                "default_patient_id": self.patient_id.id,
                "search_default_occurrence_hour": True,
            }
        )
        action["context"] = ctx
        return action

    @property
    def _workflow_name(self):
        return self.category_id.name or self._name

    @property
    def _workflow_summary(self):
        return "{} {} {}".format(self.type_id.name, self.value, self.unit_id.name or "")

    @api.model
    def garbage_collect(self):
        limit_date = fields.datetime.utcnow() - get_timedelta(1, "day")
        return self.search(
            [
                ("value", "=", False),
                ("write_date", "<", limit_date),
            ]
        ).unlink()
