#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class VitalSign(models.Model):
    _name = "ni.observation.vitalsign"
    _description = "Vital Signs"
    _inherit = ["ni.observation.base"]

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

    @api.depends("bp_s", "bp_d")
    def _compute_interpretation(self):
        for rec in self:
            rec.bp_s_interpretation_id = rec.interpretation_for("bp_s")
            rec.bp_d_interpretation_id = rec.interpretation_for("bp_d")
