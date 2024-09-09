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

    _sql_constraints = [
        (
            "type__uniq",
            "unique (sheet_id, type_id)",
            "Duplication observation type!",
        ),
    ]

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
