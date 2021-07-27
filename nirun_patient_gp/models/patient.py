#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    gp_id = fields.Many2one(
        "res.partner", "General Practitioner", compute="_compute_gp", store=True
    )
    gp_ids = fields.One2many("ni.patient.gp", "patient_id")
    gp_hospital_id = fields.Many2one(
        "res.partner",
        "Hospital",
        domain=[("is_company", "=", True)],
        compute="_compute_gp",
        store=True,
    )

    @api.depends("gp_ids.practitioner_id", "gp_ids.practitioner_company_id")
    def _compute_gp(self):
        for rec in self:
            if len(rec.gp_ids) == 0:
                continue
            gp = rec.gp_ids[0]
            rec.update(
                {
                    "gp_id": gp.practitioner_id,
                    "gp_hospital_id": gp.practitioner_company_id,
                }
            )

    @api.onchange("gp_id")
    def onchange_gp_id(self):
        for rec in self:
            if rec.gp_id and rec.gp_id.parent_id:
                rec.gp_hospital_id = rec.gp_id.parent_id
