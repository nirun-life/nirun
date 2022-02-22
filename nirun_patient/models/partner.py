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

    @api.model
    def default_get(self, default_fields):
        """
        We Found that 'default_parent_id' for res.partner have a
        chance to mess up with mail.message's parent_id
        make user unable to create partner.

        So, Workaround solution is use `default_partner_parent_id` instead
        """
        values = super().default_get(default_fields)
        if self._context.get("default_partner_parent_id"):
            values["parent_id"] = self._context.get("default_partner_parent_id")
        return values

    @api.depends("patient_ids")
    def _compute_patient(self):
        for rec in self:
            rec.patient = bool(rec.patient_ids)
            rec.patient_id = rec.patient_ids.filtered(
                lambda p: p.company_id == self.env.company
            )
