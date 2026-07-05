#  Copyright (c) 2025 NSTDA

from odoo import fields, models


class Users(models.Model):
    _inherit = ["res.users", "ni.my.area.mixin"]
    _name = "res.users"

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

    def name_get(self):
        is_admin = self.env.user.has_group("ni_patient.group_admin")
        is_dev = self.env.user.has_group("base.group_no_one")
        result = []
        for user in self:
            name = user.employee_id.name or user.name
            if is_admin and user.name and user.name.lower() != name.lower():
                name = f"{name} ({user.name})"
            if is_dev and user.login and user.login != user.name:
                name = f"{name} [{user.login}]"
            result.append((user.id, name))
        return result

    def _get_employee_fields_to_sync(self):
        fields = super()._get_employee_fields_to_sync()
        fields += ["city_ids", "state_ids", "country_id"]
        return fields
