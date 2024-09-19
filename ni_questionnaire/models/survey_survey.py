#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class Survey(models.Model):
    _name = "survey.survey"
    _inherit = ["survey.survey", "ni.specialty.mixin"]

    subject_type = fields.Selection(
        selection=[
            ("res.partner", "Partner"),
            ("res.users", "Users"),
            ("ni.patient", "Patient"),
            ("ni.encounter", "Encounter"),
        ],
    )

    observation_type_id = fields.Many2one(
        "ni.observation.type", domain=[("value_type", "in", ["int", "float"])]
    )
    observation_score_type = fields.Selection(
        [("percentage", "Percentage"), ("raw", "Raw Value")],
        default="raw",
        required=True,
    )

    question_group_ids = fields.One2many("survey.question.group", "survey_id")

    def action_sync_observation_range(self):
        if not self.observation_type_id:
            raise ValidationError(_("Please specify observation"))
        if not self.observation_type_id.ref_range_ids:
            raise ValidationError(_("Observation not have reference range"))

        _max = self.observation_type_id.max
        self.grade_ids = [fields.Command.clear()] + [
            fields.Command.create(
                {
                    "name": ref.interpretation_id.name,
                    "gender": ref.gender,
                    "age_low": ref.age_low,
                    "age_high": ref.age_high,
                    "low": (ref.low / _max) * 100,
                    "high": (ref.high / _max) * 100,
                    "color_class": ref.interpretation_id.display_class,
                }
            )
            for ref in self.observation_type_id.ref_range_ids
        ]

    @api.constrains("observation_type_id")
    def _check_observation_type(self):
        for rec in self:
            if rec.observation_type_id and rec.observation_type_id.value_type not in [
                "int",
                "float",
            ]:
                raise UserError(_("Observation but be Int or Float"))
