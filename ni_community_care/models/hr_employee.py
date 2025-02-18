#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    def _sync_user(self, user, employee_has_image=False):
        vals = super()._sync_user(user, employee_has_image)
        if user.country_id:
            vals["country_id"] = user.country_id.id
        if user.state_ids:
            vals["state_ids"] = [fields.Command.set(user.state_ids.ids)]
        if user.city_ids:
            vals["city_ids"] = [fields.Command.set(user.city_ids.ids)]
        return vals
