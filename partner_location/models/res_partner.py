#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    google_maps_url = fields.Char(compute="_compute_google_maps_url")

    @api.depends("partner_latitude", "partner_longitude")
    def _compute_google_maps_url(self):
        for rec in self:
            if not rec.partner_latitude or not rec.partner_longitude:
                rec.google_maps_url = None
            else:
                rec.google_maps_url = (
                    "https://www.google.com/maps?saddr=My Location&daddr=%s,%s"
                    % (rec.partner_latitude, rec.partner_longitude)
                )

    def action_google_maps_dir(self):
        return {
            "type": "ir.actions.act_url",
            "url": self.google_maps_url,
            "name": _("Google Maps Directions"),
        }
