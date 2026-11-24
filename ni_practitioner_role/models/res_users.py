#  Copyright (c) 2023 NSTDA

from odoo import fields, models
from odoo.exceptions import AccessDenied


class Users(models.Model):
    _inherit = "res.users"

    verified = fields.Boolean(default=True)

    def action_verify(self):
        for rec in self:
            rec.verified = True
            if not rec.employee_id:
                rec.action_create_employee()
                emp = rec.employee_id
                emp.license_no = rec.login
                emp.category_ids = rec.user_role_ids.mapped("employee_category_ids")

    def action_verify_employee(self):
        for rec in self:
            rec.action_create_employee()
            rec.employee_id.license_no = rec.login

    def _check_credentials(self, credential, env):
        if not self.verified:
            raise AccessDenied(self.env._("Waiting for verify"))
        return super()._check_credentials(credential, env)
