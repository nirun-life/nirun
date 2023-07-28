#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    google_maps_url = fields.Char(related="partner_id.google_maps_url")
    partner_latitude = fields.Float(
        related="partner_id.partner_latitude", readonly=False
    )
    partner_longitude = fields.Float(
        related="partner_id.partner_longitude", readonly=False
    )

    def action_google_maps_dir(self):
        return self.partner_id.action_google_maps_dir()
