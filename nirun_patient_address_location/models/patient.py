#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Patient(models.Model):
    _inherit = "ni.patient"

    zip_id = fields.Many2one(related="partner_id.zip_id", readonly=False, index=True)
    city_id = fields.Many2one(
        related="partner_id.city_id", readonly=False, index=True
    )  # add index for performance

    @api.onchange("city_id")
    def _onchange_city_id(self):
        if not self.zip_id:
            super()._onchange_city_id()
        if self.zip_id and self.city_id != self.zip_id.city_id:
            self.update({"zip_id": False, "zip": False, "city": False})
        if self.city_id and self.partner_id.country_enforce_cities:
            return {"domain": {"zip_id": [("city_id", "=", self.city_id.id)]}}
        return {"domain": {"zip_id": []}}

    @api.onchange("country_id")
    def _onchange_country_id(self):
        res = self.partner_id._onchange_country_id()
        if self.zip_id and self.zip_id.city_id.country_id != self.country_id:
            self.zip_id = False
        return res

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        if self.zip_id:
            vals = {
                "city_id": self.zip_id.city_id,
                "zip": self.zip_id.name,
                "city": self.zip_id.city_id.name,
            }
            if self.zip_id.city_id.country_id:
                vals.update({"country_id": self.zip_id.city_id.country_id})
            if self.zip_id.city_id.state_id:
                vals.update({"state_id": self.zip_id.city_id.state_id})
            self.update(vals)
        elif not self.partner_id or not self.partner_id.country_enforce_cities:
            self.city_id = False

    @api.constrains("zip_id", "country_id", "city_id", "state_id")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.zip_id:
                continue
            if rec.zip_id.city_id.state_id != rec.state_id:
                raise ValidationError(
                    _("The state of the partner %s differs from that in " "location %s")
                    % (rec.name, rec.zip_id.name)
                )
            if rec.zip_id.city_id.country_id != rec.country_id:
                raise ValidationError(
                    _(
                        "The country of the partner %s differs from that in "
                        "location %s"
                    )
                    % (rec.name, rec.zip_id.name)
                )
            if rec.zip_id.city_id != rec.city_id:
                raise ValidationError(
                    _("The city of partner %s differs from that in " "location %s")
                    % (rec.name, rec.zip_id.name)
                )

    @api.onchange("state_id")
    def _onchange_state_id(self):
        vals = {}
        if self.state_id.country_id:
            vals.update({"country_id": self.state_id.country_id})
        if self.zip_id and self.state_id != self.zip_id.city_id.state_id:
            vals.update({"zip_id": False, "zip": False, "city": False})
        self.update(vals)
