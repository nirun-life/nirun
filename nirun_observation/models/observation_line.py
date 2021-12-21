#  Copyright (c) 2021 Piruin P.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ObservationLine(models.Model):
    _name = "ni.observation.line"
    _description = "Observation Line"
    _order = "effective_date DESC,patient_id,sequence"

    observation_id = fields.Many2one(
        "ni.observation", required=True, readonly=True, index=True, ondelete="cascade",
    )
    company_id = fields.Many2one(
        related="observation_id.company_id", store=True, readonly=True
    )
    patient_id = fields.Many2one(
        related="observation_id.patient_id", store=True, readonly=True
    )
    effective_date = fields.Datetime(
        related="observation_id.effective_date", store=True, readonly=True
    )
    type_id = fields.Many2one("ni.observation.type", required=True)
    sequence = fields.Integer(related="type_id.sequence")
    category_id = fields.Many2one(related="type_id.category_id", readonly=True)
    value = fields.Float(group_operator="avg")
    unit = fields.Many2one(related="type_id.unit")
    interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        ondelete="restrict",
        readonly=True,
        require=False,
        store=True,
        default=None,
    )
    display_class = fields.Selection(
        [
            ("text", "Text"),
            ("muted", "Muted"),
            ("info", "Info"),
            ("primary", "Primary"),
            ("success", "Success"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        related="interpretation_id.display_class",
        default="text",
    )

    _sql_constraints = [
        (
            "type__uniq",
            "unique (observation_id, type_id)",
            "Duplication observation type!",
        ),
    ]

    @api.onchange("type_id")
    def _onchange_type(self):
        self.update({"interpretation_id": None})
        self._compute_interpretation()

    @api.depends("value")
    def _compute_interpretation(self):
        for rec in self:
            rec.interpretation_id = rec._interpretation_for()

    def _interpretation_for(self):
        if self.type_id.ref_range_count == 0:
            return None

        ranges = self.env["ni.observation.reference.range"].search(
            [
                ("type_id", "=", self.type_id.id),
                ("low", "<=", self.value),
                ("high", ">", self.value),
            ],
            limit=1,
        )
        if ranges:
            return ranges[0].interpretation_id
        else:
            return self.env.ref("nirun_observation.interpretation_EX")

    @api.constrains("value")
    def check_input_range(self):
        for rec in self:
            if not (rec.type_id.min <= rec.value <= rec.type_id.max):
                raise ValidationError(
                    _("%s %s is out of acceptable range [%d-%d]")
                    % (rec.type_id.name, rec.value, rec.type_id.min, rec.type_id.max)
                )

    def view_graph(self):
        action_rec = self.env.ref("nirun_observation.ob_line_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.patient_id.id,
                "search_default_type_id": self.type_id.id,
                "default_patient_id": self.patient_id.id,
            }
        )
        action["context"] = ctx
        return action
