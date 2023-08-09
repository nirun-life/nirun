#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    coverage_type_ids = fields.Many2many("ni.coverage.type")
    coverage_ids = fields.One2many("ni.coverage", "patient_id", string="Coverages")
    coverage_id = fields.Many2one(
        "ni.coverage",
        string="Coverage (Main)",
        compute="_compute_coverage",
        store=True,
        compute_sudo=True,
    )

    @api.depends("coverage_ids")
    def _compute_coverage(self):
        for rec in self:
            if rec.coverage_ids:
                coverages = rec.coverage_ids.sorted("sequence")
                rec.coverage_id = coverages[0]
            else:
                rec.coverage_id = None
