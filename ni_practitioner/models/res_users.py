# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class User(models.Model):
    _inherit = ["res.users"]

    license_id = fields.Many2one(
        related="employee_id.license_id",
        readonly=False,
        domain="[('employee_id', '=', employee_id), ('identifier', '!=', False)]",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["license_id"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["license_id"]
