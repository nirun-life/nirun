#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class VitalSign(models.Model):
    _name = "ni.observation.vitalsign"
    _description = "Vital Signs"
    _inherit = ["ni.observation.base"]

    _codes = ["bp_s", "bp_d", "heart_rate"]
    _input_range = [
        ("bp_s", 0.0, 300.0),
        ("bp_d", 0.0, 300.0),
        ("heart_rate", 0.0, 200.0),
    ]

    bp_s = fields.Float("SYS", digits=(8, 2))
    bp_s_interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        ondelete="restrict",
        readonly=True,
        store=True,
    )
    bp_d = fields.Float("DIA", digits=(8, 2))
    bp_d_interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        ondelete="restrict",
        readonly=True,
        store=True,
    )
    heart_rate = fields.Float("PUL", digits=(8, 2))
    heart_rate_interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        ondelete="restrict",
        readonly=True,
        store=True,
    )

    @api.constrains(*_codes)
    def _check_input_range(self):
        super().check_input_range(self._input_range)
