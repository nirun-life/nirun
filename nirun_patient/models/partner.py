#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    patient = fields.Boolean(
        compute="_compute_patient",
        store=True,
        help="Check this box if this contact is an Patient.",
        compute_sudo=True,
        groups="nirun_patient.group_user",
    )
    patient_ids = fields.One2many(
        "ni.patient", "partner_id", "Patient Records", groups="nirun_patient.group_user"
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient Record",
        compute="_compute_patient",
        compute_sudo=True,
        groups="nirun_patient.group_user",
    )

    @api.depends("patient_ids")
    def _compute_patient(self):
        for rec in self:
            rec.patient = bool(rec.patient_ids)
            rec.patient_id = rec.patient_ids.filtered(
                lambda p: p.company_id == self.env.company
            )

    def open_patient_record(self):
        return {
            "name": "Patient",
            "type": "ir.actions.act_window",
            "res_model": "ni.patient",
            "res_id": self.patient_id.id,
            "view_mode": "form",
        }
