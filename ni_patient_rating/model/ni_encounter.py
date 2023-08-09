#  Copyright (c) 2023 NSTDA
from odoo import _, api, fields, models


class Encounter(models.Model):
    _name = "ni.encounter"
    _inherit = ["ni.encounter", "rating.mixin"]

    rating_last_value = fields.Float("Rating")
    rating_link = fields.Char("Link", compute="_compute_rating_link")
    rating_qrcode = fields.Char("QR Code")

    @api.depends("rating_ids")
    def _compute_rating_link(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            if not rec.rating_count:
                rec.rating_link = "%s/rate/%s/5" % (
                    base_url,
                    rec._rating_get_access_token(),
                )
                rec.rating_qrcode = "%s/report/barcode/QR/%s" % (
                    base_url,
                    rec.rating_link,
                )
            else:
                rec.rating_link = None
                rec.rating_qrcode = None

    def action_rating(self):
        return {
            "type": "ir.actions.act_url",
            "url": self.rating_link or "/rate/%s/5" % self._rating_get_access_token(),
            "name": _("Rating"),
        }

    def action_send_rating_mail(self):
        template = self.env.ref("ni_patient_rating.rating_ni_encounter_email_template")
        self.rating_send_request(template)
