#  Copyright (c) 2025 NSTDA

from odoo import api, fields, models


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

    my_area = fields.Boolean(compute="_compute_my_area", search="_search_my_area")

    @api.depends("city_ids")
    def _compute_my_area(self):
        my_cities = self.env.user.city_ids.ids
        for rec in self:
            rec.my_area = bool(set(rec.city_ids.ids) & set(my_cities))

    def _search_my_area(self, operator, value):
        my_city_ids = self.env.user.city_ids.ids
        if not my_city_ids:
            return [("id", "=", 0)]
        return [("city_ids", "in", my_city_ids)]

    def action_add_response_state_cities(self):
        city = self.env["res.city"].search([("state_id", "in", self.state_ids.ids)])
        if city:
            self.city_ids = [fields.Command.set(city.ids)]

    def _get_employee_fields_to_sync(self):
        fields = super()._get_employee_fields_to_sync()
        fields += ["city_ids", "state_ids", "country_id"]
        return fields
