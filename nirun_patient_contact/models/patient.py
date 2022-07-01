#  Copyright (c) 2021 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Patient(models.Model):
    _inherit = "ni.patient"

    contact_id = fields.Many2one("res.partner", "Primary Contact", ondelete="set null")
    contact_id_2 = fields.Many2one(
        "res.partner", "Secondary Contact", ondelete="set null"
    )
    contact_ids = fields.One2many(
        related="partner_id.child_ids", string="Contacts", readonly=False
    )
    contact_na = fields.Boolean("Contact N/A", default=False)

    @api.onchange("contact_id", "contact_id_2")
    def _onchange_contact_id_1_id_2(self):
        if self.contact_id or self.contact_id_2:
            self.contact_na = False

    @api.constrains("contact_id", "contact_id_2", "contact_na")
    def check_contact_id(self):
        for rec in self:
            if rec.contact_na and (rec.contact_id or rec.contact_id_2):
                raise UserError(
                    _("Primary & Secondary contact must be empty if N/A is checked")
                )
            if rec.contact_id and rec.contact_id == rec.contact_id_2:
                raise UserError(
                    _("Primary Contact and secondary should not be same person")
                )
