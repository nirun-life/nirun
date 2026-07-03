#  Copyright (c) 2021 NSTDA
from odoo import _, api, fields, models, tools
from odoo.tools.date_utils import get_timedelta

_VALUE_FIELDS = frozenset({"value", "value_float", "value_int", "value_char"})


class Observation(models.Model):
    _name = "ni.observation"
    _description = "Observation"
    _inherit = ["ni.workflow.event.mixin", "ni.observation.abstract"]
    _order = "occurrence DESC,patient_id,sequence"

    _parent_store = True

    parent_id = fields.Many2one(
        "ni.observation", "Component of", index=True, ondelete="set null"
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many("ni.observation", "parent_id", "Components")
    child_count = fields.Integer("Number of Components", compute="_compute_child_count")

    state = fields.Selection(default="completed")

    @api.depends("child_ids")
    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

    history_ids = fields.One2many(
        "ni.observation", string="ประวัติ", compute="_compute_history"
    )
    history_count = fields.Integer(compute="_compute_history")

    def _compute_history(self):
        for rec in self:
            rec.history_ids = self.env["ni.observation"].search(
                [
                    ("patient_id", "=", self.patient_id.id),
                    ("type_id", "=", self.type_id.get_display_type().ids),
                    ("value", "!=", False),
                ],
                order="occurrence desc",
            )
            rec.history_count = len(rec.history_ids)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("skip_compute_eval"):
            records.mapped("sheet_id").filtered("id")._eval_compute_types()
        return records

    def write(self, vals):
        result = super().write(vals)
        if (
            result
            and not self.env.context.get("skip_compute_eval")
            and _VALUE_FIELDS.intersection(vals)
        ):
            self.mapped("sheet_id").filtered("id")._eval_compute_types()
        return result

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

    compute = fields.Boolean(related="type_id.compute")

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
            if (
                not rec.type_id
                or not rec.type_id.compare
                or rec.type_id.value_type not in ["int", "float"]
            ):
                rec.update({"compare": None, "compare_interpret": None})
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
                rec.update({"compare": None, "compare_interpret": None})
                continue

            # Get the value based on the type_id's value_type
            field_name = f"value_{rec.type_id.value_type}"
            current_value = getattr(rec, field_name)
            previous_value = getattr(prev, field_name)

            if current_value == previous_value:
                rec.update({"compare": "eq", "compare_interpret": "neutral"})

            elif current_value < previous_value:
                rec.update(
                    {
                        "compare": "lt",
                        "compare_interpret": "better"
                        if rec.type_id.compare == "low"
                        else "worsen",
                    }
                )
            else:
                rec.update(
                    {
                        "compare": "gt",
                        "compare_interpret": "better"
                        if rec.type_id.compare == "high"
                        else "worsen",
                    }
                )

    def init(self):
        tools.create_index(
            self._cr,
            "ni_observation__patient__ob_type__idx",
            self._table,
            ["patient_id", "type_id", "occurrence DESC", "id"],
        )
        tools.create_index(
            self._cr,
            "ni_observation__encounter__ob_type__idx",
            self._table,
            ["encounter_id", "type_id", "occurrence DESC", "id"],
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
                "default_patient_id": self.patient_id.id,
                "search_default_occurrence_hour": True,
                "value_type": self.type_id.value_type,
                "graph_default_type": self.type_id.graph_type,
                "type": self.type_id.graph_type,
                "stacked": True,
                "graph_view_ref": self.type_id.get_graph_view_ref(),
            }
        )
        action["context"] = ctx
        action["domain"] = [
            ("patient_id", "=", self.patient_id.id),
            ("type_id", "in", self.type_id.get_display_type().ids),
        ]
        return action

    @property
    def _workflow_name(self):
        return self.category_id.name or self._name

    @property
    def _workflow_summary(self):
        return "{} {} {}".format(self.type_id.name, self.value, self.unit_id.name or "")

    @api.model
    def garbage_collect(self, delta_qty=1, deltay_granularity="day"):
        limit_date = fields.Datetime.now() - get_timedelta(
            delta_qty, deltay_granularity
        )
        return self.search(
            [
                ("value", "=", False),
                ("write_date", "<", limit_date),
            ]
        ).unlink()
