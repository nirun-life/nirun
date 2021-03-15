#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class VitalSign(models.Model):
    _name = "ni.observation.vitalsign"
    _description = "Vital Signs"
    _inherit = ["ni.observation.base"]

    bp_s = fields.Float("Blood Pressure Systolic")
    bp_s_interpretation_id = fields.Many2one(
        "ni.observation.interpretation", readonly=True, store=True,
    )
    bp_d = fields.Float("Blood Pressure Diastolic")
    bp_d_interpretation_id = fields.Many2one(
        "ni.observation.interpretation", readonly=True, store=True,
    )
