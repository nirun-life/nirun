#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class VitalSign(models.Model):
    _name = "ni.observation.vitalsign"
    _description = "Vital Signs"
    _inherit = ["ni.observation.base"]

    _codes = ["bp_s", "bp_d"]

    bp_s = fields.Float("Blood Pressure Systolic")
    bp_s_interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        readonly=True,
        store=True,
    )
    bp_d = fields.Float("Blood Pressure Diastolic")
    bp_d_interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        compute="_compute_interpretation",
        readonly=True,
        store=True,
    )
