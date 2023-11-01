#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    patient = fields.Boolean(
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
        compute="_compute_patient",
        compute_sudo=True,
        groups="ni_patient.group_viewer",
    )
    identification_id = fields.Char(
        string="Identification No",
        copy=False,
        tracking=True,
        help="ID related to patient's nationality",
    )

    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if name:
            name = name.split(" / ")[-1]
        if not (name == "" and operator == "ilike"):
            args += [
                "|",
                "|",
                "|",
                ("name", operator, name),
                ("mobile", "=", name),
                ("phone", "=", name),
                ("identification_id", "=", name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

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
