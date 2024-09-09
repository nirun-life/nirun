#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class ObservationSheet(models.Model):
    _name = "ni.observation.sheet"
    _description = "Observation Sheet"
    _inherit = ["ni.patient.res", "ni.identifier.mixin"]
    _order = "occurrence DESC"
    _identifier_ts_field = "period_start"

    name = fields.Char(
        "Identifier",
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._identifier_default,
    )
    performer_ref = fields.Reference(
        [("ni.patient", "Patient"), ("hr.employee", "Practitioner")],
        string="Performer",
        required=False,
        index=True,
    )
    occurrence = fields.Datetime(
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
        if result and vals.get("occurrence"):
            for rec in self:
                rec.observation_ids.write({"occurrence": rec.occurrence})
        return result

    def action_patient_observation_graph(self):
        action_rec = self.env.ref("ni_observation.ni_observation_action").sudo()
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
                [("category_id", "in", self.category_ids.ids), ("compute", "=", False)],
                order="category_id, sequence, id",
            )
            line_types = self.observation_ids.mapped("type_id")
            section_name = self.observation_ids.filtered("display_type").mapped("name")
            line = []
            for cat in self.category_ids:
                if cat.name not in section_name and len(self.category_ids) > 1:
                    line.append(self.line_section(cat))
                line = line + [
                    self.line_data(t)
                    for t in types.filtered(lambda s: s.category_id.id == cat.id)
                    if t not in line_types
                ]
            # Apply sequence to each line
            for i in range(len(line)):
                line[i]["sequence"] = i
            self.update({"observation_ids": [(0, 0, data) for data in line]})

    def line_section(self, category_id):
        return {
            "sheet_id": self.id,
            "title": category_id.name,
            "patient_id": self.patient_id.id,
            "occurrence": self.occurrence,
            "encounter_id": self.encounter_id.id,
            "display_type": "line_section",
        }

    def line_data(self, type_id):
        return {
            "sheet_id": self.id,
            "occurrence": self.occurrence,
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "type_id": type_id.id,
            "value_type": type_id.value_type,
            "sequence": type_id.sequence,
        }
