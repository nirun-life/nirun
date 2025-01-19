#  Copyright (c) 2025 NSTDA

from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    state_ids = fields.Many2many(
        "res.country.state",
        "res_user_response_state",
        "user_id",
        "state_id",
        "จังหวัดที่รับผิดชอบ",
        domain="[('country_id', '=', country_id)]",
    )
    city_ids = fields.Many2many(
        "res.city",
        "res_user_response_city",
        "user_id",
        "city_id",
        "พื้นที่รับผิดชอบ",
        domain="[('state_id', 'in', state_ids)]",
    )

    def action_add_response_state_cities(self):
        city = self.env["res.city"].search([("state_id", "in", self.state_ids.ids)])
        if city:
            self.city_ids = [fields.Command.set(city.ids)]
