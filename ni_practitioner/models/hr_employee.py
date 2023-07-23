#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    license_id = fields.Many2one(
        "hr.resume.line",
        domain="[('employee_id', '=', id), ('identifier', '!=', False)]",
    )
    license_default_id = fields.Many2one(
        "hr.resume.line", compute="_compute_default_license_id", store=True
    )

    @api.depends("resume_line_ids", "license_id")
    def _compute_default_license_id(self):
        for rec in self:
            if rec.license_id:
                rec.license_default_id = rec.license_id
            else:
                _license = self.env["hr.resume.line"].search(
                    [
                        ("employee_id", "=", rec.id),
                        ("identifier", "!=", False),
                    ],
                    limit=1,
                )
                if _license:
                    rec.license_default_id = _license[0]
