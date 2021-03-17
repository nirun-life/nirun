#  Copyright (c) 2021 Piruin P.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ObservationLine(models.Model):
    _name = "ni.observation.line"
    _description = "Observation Line"
    _order = "effective_date DESC,patient_id,sequence"

    observation_id = fields.Many2one(
        "ni.observation.base", required=True, readonly=True, index=True
    )
    patient_id = fields.Many2one(
        related="observation_id.patient_id", store=True, readonly=True
    )
    effective_date = fields.Datetime(
        related="observation_id.effective_date", store=True, readonly=True
    )
    type_id = fields.Many2one("ni.observation.type")
    sequence = fields.Integer(related="type_id.sequence")
    category_id = fields.Many2one(related="type_id.category_id", readonly=True)
    value = fields.Float(group_operator="avg")
    unit = fields.Many2one(related="type_id.unit")
    interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        ondelete="restrict",
        readonly=True,
        store=True,
    )
    display_class = fields.Selection(
        [
            ("muted", "Muted"),
            ("info", "Info"),
            ("primary", "Primary"),
            ("success", "Success"),
            ("warning", "Warning"),
            ("danger", "Danger"),
        ],
        related="interpretation_id.display_class",
        default="info",
    )

    @api.depends("value")
    def _compute_interpretation(self):
        for rec in self:
            rec.interpretation_id = rec._interpretation_for()

    def _interpretation_for(self):
        ranges = self.env["ni.observation.reference.range"].search(
            [
                ("type_id", "=", self.type_id.id),
                ("low", "<=", self.value),
                ("high", ">", self.value),
            ],
            limit=1,
        )
        return (
            ranges[0].interpretation_id
            if ranges
            else self.env.ref("nirun_observation.interpretation_EX")
        )

    @api.constrains("value")
    def check_input_range(self):
        for rec in self:
            if not (rec.type_id.min <= rec.value <= rec.type_id.max):
                raise ValidationError(
                    _("%s %s is out of acceptable range [%d-%d]")
                    % (rec.type_id.name, rec.value, rec.type_id.min, rec.type_id.max)
                )
