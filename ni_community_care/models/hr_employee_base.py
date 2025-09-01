#  Copyright (c) 2025 NSTDA
from odoo import api, fields, models


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

    sub_district_code = fields.Char(
        compute="_compute_sub_district_code",
        inverse="_inverse_sub_district_code",
        store=True,
        index=True,
    )

    @api.depends("city_ids")
    def _compute_sub_district_code(self):
        for rec in self:
            if not rec.city_ids:
                rec.sub_district_code = None
                continue
            city_zip = self.env["res.city.zip"].search(
                [
                    ("city_id", "in", rec.city_ids[0].ids),
                ],
                limit=1,
            )
            rec.sub_district_code = city_zip.sub_district_code

    def _inverse_sub_district_code(self):
        for rec in self:
            city_zip = self.env["res.city.zip"].search(
                [("sub_district_code", "=", rec.sub_district_code)], limit=1
            )
            if city_zip:
                rec.state_ids = [fields.Command.link(city_zip.state_id.id)]
                rec.city_ids = [fields.Command.link(city_zip.city_id.id)]

    def action_add_response_state_cities(self):
        city = self.env["res.city"].search([("state_id", "in", self.state_ids.ids)])
        if city:
            self.city_ids = [fields.Command.set(city.ids)]
