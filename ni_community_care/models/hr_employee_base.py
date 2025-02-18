#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class EmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    country_id = fields.Many2one(
        "res.country", default=lambda self: self.env.ref("base.th")
    )

    state_ids = fields.Many2many(
        "res.country.state",
        "hr_employee_response_state",
        "employee_id",
        "state_id",
        "จังหวัดที่รับผิดชอบ",
        domain="[('country_id', '=', country_id)]",
    )
    city_ids = fields.Many2many(
        "res.city",
        "hr_employee_response_city",
        "employee_id",
        "city_id",
        "พื้นที่รับผิดชอบ",
        domain="[('state_id', 'in', state_ids)]",
    )

    def action_add_response_state_cities(self):
        city = self.env["res.city"].search([("state_id", "in", self.state_ids.ids)])
        if city:
            self.city_ids = [fields.Command.set(city.ids)]
