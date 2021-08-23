#  Copyright (c) 2021 Piruin P.
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

    @api.constrains("contact_id", "contact_id_2")
    def check_contact_id(self):
        for rec in self:
            if rec.contact_id and rec.contact_id == rec.contact_id_2:
                raise UserError(
                    _("Primary Contact and secondary should not be same person")
                )
