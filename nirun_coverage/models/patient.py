#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    coverage_ids = fields.One2many("ni.coverage", "patient_id", string="Coverages")
    coverage_id = fields.Many2one(
        "ni.coverage", string="Coverage (Main)", compute="_compute_coverage", store=True
    )

    @api.depends("coverage_ids")
    def _compute_coverage(self):
        for rec in self:
            if rec.coverage_ids:
                coverages = rec.coverage_ids.sorted("sequence")
                rec.coverage_id = coverages[0]
