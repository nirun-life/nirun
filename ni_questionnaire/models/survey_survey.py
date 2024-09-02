#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Survey(models.Model):
    _inherit = "survey.survey"

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

    @api.constrains("observation_type_id")
    def _check_observation_type(self):
        for rec in self:
            if rec.observation_type_id and rec.observation_type_id.value_type not in [
                "int",
                "float",
            ]:
                raise UserError(_("Observation but be Int or Float"))
