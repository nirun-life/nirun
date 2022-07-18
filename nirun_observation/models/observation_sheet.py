#  Copyright (c) 2021 NSTDA
from odoo import fields, models


class ObservationSheet(models.Model):
    _name = "ni.observation.sheet"
    _description = "Observation Sheet"
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
    observation_ids = fields.One2many("ni.observation", "sheet_id")

    category_ids = fields.Many2many(
        "ni.observation.category",
        "ni_observation_sheet_category_rel",
        "sheet_id",
        "category_id",
        required=False,
    )

    def write(self, vals):
        result = super(ObservationSheet, self).write(vals)
        if result and vals.get("effective_date"):
            for rec in self:
                rec.observation_ids.write({"effective_date": rec.effective_date})
        return result

    def action_patient_observation_graph(self):
        action_rec = self.env.ref("nirun_observation.ob_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.patient_id.id,
                "default_patient_id": self.patient_id.id,
            }
        )
        action["context"] = ctx
        return action

    def action_line_by_category_ids(self):
        if self.category_ids:
            types = self.env["ni.observation.type"].search(
                [("category_id", "in", self.category_ids.ids)],
                order="category_id, sequence, id",
            )
            line_types = self.observation_ids.mapped("type_id")
            self.update(
                {
                    "observation_ids": [
                        (0, 0, self.line_data(t)) for t in types if t not in line_types
                    ]
                }
            )

    def line_data(self, type_id):
        return {
            "sheet_id": self.id,
            "effective_date": self.effective_date,
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "type_id": type_id.id,
            "sequence": type_id.sequence,
        }
