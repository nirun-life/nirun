#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class Observation(models.Model):
    _name = "ni.observation"
    _description = "Observation"
    _inherit = ["ni.patient.res", "ir.sequence.mixin"]
    _order = "effective_date DESC"

    _sequence_ts_field = "effective_date"
    name = fields.Char(
        "Identifier",
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._sequence_default,
    )
    patient_age_years = fields.Integer(related="patient_id.age_years")
    performer_ref = fields.Reference(
        [("ni.patient", "Patient"), ("hr.employee", "Practitioner")],
        string="Performer",
        required=False,
        index=True,
    )
    effective_date = fields.Datetime(
        required=True, default=lambda _: fields.Datetime.now(), index=True
    )
    active = fields.Boolean(default=True)
    note = fields.Text()
    lines = fields.One2many("ni.observation.line", "observation_id")

    def action_patient_observation_graph(self):
        action_rec = self.env.ref("nirun_observation.ob_line_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.ids[0],
                "default_patient_id": self.ids[0],
                "graph_mode": "line",
            }
        )
        action["context"] = ctx
        return action
