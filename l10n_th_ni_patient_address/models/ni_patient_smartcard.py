#  Copyright (c) 2026 NSTDA
from odoo import fields, models


class PatientSmartcard(models.Model):
    _inherit = "ni.patient.smartcard"

    city_id = fields.Many2one("res.city")
    zip_id = fields.Many2one("res.city.zip")
    state_id = fields.Many2one("res.country.state")
    country_id = fields.Many2one("res.country")

    def _extract_card_info(self):
        super()._extract_card_info()

        names = self.card_data.split("#")
        city_name = ", ".join([names[i] for i in range(14, 16) if names[i]])
        city_name = city_name.replace("ตำบล", "ต.")
        city_name = city_name.replace("อำเภอ", "อ.")
        city = self.env["res.city"].search([("name", "=", city_name)], limit=1)
        if city:
            self.city_id = city
            self.zip_id = city.zip_ids[0]
            self.state_id = city.state_id
            self.country_id = city.country_id
