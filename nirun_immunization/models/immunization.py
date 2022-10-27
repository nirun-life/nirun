#  Copyright (c) 2022. NSTDA

from odoo import api, fields, models


class Immunization(models.Model):
    _name = "ni.immunization"
    _inherit = ["ni.patient.res", "mail.thread"]

    _rec_name = "vaccine_id"
    _description = "Immunization"

    occurrence_date = fields.Date(compute="_compute_occurrence_date", store=True)
    occurrence = fields.Datetime(
        required=True, default=lambda _: fields.Datetime.now(), tracking=True
    )
    administering_id = fields.Many2one(
        "res.partner", "Administering Provider", tracking=True
    )

    vaccine_id = fields.Many2one("ni.vaccine", required=True, tracking=True)
    vaccine_manufacturer_ids = fields.Many2many(related="vaccine_id.manufacturer_ids")
    vaccine_manufacturer_filter = fields.Integer(
        related="vaccine_id.manufacturer_filter"
    )
    manufacturer_id = fields.Many2one(
        "res.partner",
        tracking=True,
        domain="['|', "
        "('id', 'in', vaccine_manufacturer_ids), "
        "('id', '>', vaccine_manufacturer_filter)]",
    )
    lot_number = fields.Char(help="Vaccine lot number", tracking=True)
    expiration_date = fields.Date(help="Vaccine expiration date", tracking=True)
    note = fields.Text()

    @api.depends("occurrence")
    def _compute_occurrence_date(self):
        for rec in self:
            rec.occurrence_date = rec.occurrence.date()
