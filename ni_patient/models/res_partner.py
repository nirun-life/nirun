#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models
from odoo.fields import Domain


class Partner(models.Model):
    _inherit = "res.partner"

    patient = fields.Boolean(
        "Is a Patient",
        compute="_compute_patient",
        store=True,
        help="Check this box if this contact is an Patient.",
        compute_sudo=True,
        groups="ni_patient.group_viewer",
    )
    patient_ids = fields.One2many(
        "ni.patient", "partner_id", "Patient Records", groups="ni_patient.group_viewer"
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient Record",
        compute="_compute_patient_id",
        compute_sudo=True,
        groups="ni_patient.group_viewer",
    )
    identification_id = fields.Char(
        string="Identification No",
        copy=False,
        tracking=True,
        help="ID related to patient's nationality",
    )

    @api.model
    def _search_display_name(self, operator, value):
        # Also find a partner by its exact phone, mobile or identification number.
        domain = super()._search_display_name(operator, value)
        if operator in ("ilike", "=ilike", "like", "=like", "=") and value:
            value = value.split(" / ")[-1]
            domain = Domain.OR(
                [
                    domain,
                    [("mobile", "=", value)],
                    [("phone", "=", value)],
                    [("identification_id", "=", value)],
                ]
            )
        return domain

    @api.model
    def default_get(self, default_fields):
        """
        We Found that 'default_parent_id' for res.partner have a
        chance to mess up with mail.message's parent_id
        make user unable to create partner.

        So, Workaround solution is use `default_partner_parent_id` instead
        """
        values = super().default_get(default_fields)
        if self.env.context.get("default_partner_parent_id"):
            values["parent_id"] = self.env.context.get("default_partner_parent_id")
        return values

    @api.depends("patient_ids")
    def _compute_patient(self):
        for rec in self:
            rec.patient = bool(rec.patient_ids)

    @api.depends("patient_ids")
    @api.depends_context("company")
    def _compute_patient_id(self):
        for rec in self:
            rec.patient_id = rec.patient_ids.filtered(
                lambda p: p.company_id == self.env.company
            )
