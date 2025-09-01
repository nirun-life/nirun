#  Copyright (c) 2025 NSTDA
from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    my_user_city_match = fields.Boolean(
        compute="_compute_my_user_city_match", search="_search_my_user_city_match"
    )

    @api.depends("city_ids")
    def _compute_my_user_city_match(self):
        my_cities = self.env.user.employee_id.city_ids.ids
        for rec in self:
            rec.my_user_city_match = bool(set(rec.city_ids.ids) & set(my_cities))

    def _search_my_user_city_match(self, operator, value):
        my_city_ids = self.env.user.employee_id.city_ids.ids
        if not my_city_ids:
            return [("id", "=", 0)]
        return [("city_ids", "in", my_city_ids)]

    def _sync_user(self, user, employee_has_image=False):
        vals = super()._sync_user(user, employee_has_image)
        if user.country_id:
            vals["country_id"] = user.country_id.id
        if user.state_ids:
            vals["state_ids"] = [fields.Command.set(user.state_ids.ids)]
        if user.city_ids:
            vals["city_ids"] = [fields.Command.set(user.city_ids.ids)]
        return vals

    @api.model
    def rewrite_user_name(self):
        employees = self.search([("user_id", "!=", False)])
        for rec in employees:
            rec.user_id.name = rec.name

    def action_create_user(self):
        vals = super().action_create_user()
        context = vals.get("context", {})
        context.update(
            {
                "default_country_id": self.country_id.id,
                "default_state_ids": [fields.Command.set(self.state_ids.ids)],
                "default_city_ids": [fields.Command.set(self.city_ids.ids)],
            }
        )
        vals["context"] = context
        return vals

    @api.onchange("user_id")
    def _onchange_user(self):
        super()._onchange_user()
        if self.user_id and self.city_ids and not self.user_id.city_ids:
            self.user_id.update(
                {
                    "country_id": self.country_id.id,
                    "state_ids": self.state_ids.ids,
                    "city_ids": self.city_ids.ids,
                }
            )
