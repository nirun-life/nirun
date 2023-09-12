#  Copyright (c) 2023 NSTDA

from odoo import _, fields, models
from odoo.exceptions import AccessDenied


class Users(models.Model):
    _inherit = "res.users"

    verified = fields.Boolean(default=True)

    def _check_credentials(self, password, env):
        if not self.verified:
            raise AccessDenied(_("Waiting for verify"))
        super(Users, self)._check_credentials(password, env)
