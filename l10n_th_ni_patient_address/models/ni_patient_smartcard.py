#  Copyright (c) 2026 NSTDA
from odoo import fields, models


class PatientSmartcard(models.Model):
    _inherit = "ni.patient.smartcard"

    city_id = fields.Many2one("res.city")
    zip_id = fields.Many2one("res.city.zip")
    state_id = fields.Many2one("res.country.state")
    country_id = fields.Many2one("res.country")

    def parse_card_data(self, card_data):
        val = super().parse_card_data(card_data)
        datas = card_data.split("#")

        city_name = ", ".join([datas[i] for i in range(14, 16) if datas[i]])
        city_name = city_name.replace("ตำบล", "ต.")
        city_name = city_name.replace("อำเภอ", "อ.")

        city = self.env["res.city"].search([("name", "=", city_name)], limit=1)
        if city:
            val.update(
                {
                    "city_id": city.id,
                    "zip_id": city.zip_ids[0].id,
                    "state_id": city.state_id.id,
                    "country_id": city.country_id.id,
                }
            )
        return val
