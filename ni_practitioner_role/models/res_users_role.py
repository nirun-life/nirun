#  Copyright (c) 2023 NSTDA

import base64
import uuid
from io import BytesIO

import qrcode

from odoo import api, fields, models


class Roles(models.Model):
    _inherit = "res.users.role"

    REGISTER_ROUTE = "practitioner/register"

    # res.groups has no color any more
    color = fields.Integer("Color Index")
    employee_category_ids = fields.Many2many("hr.employee.category")
    user_count = fields.Integer(compute="_compute_user_count")
    user_to_verify_count = fields.Integer(compute="_compute_user_count")
    access_token = fields.Char("Invitation Token", company_dependent=True)
    register_location = fields.Char(compute="_compute_register_location")
    register_qr_code = fields.Binary("QRcode", compute="_compute_register_location")

    @api.model_create_multi
    def create(self, vals_list):
        roles = super().create(vals_list)
        roles._generate_access_token()
        return roles

    def _generate_access_token(self):
        """Give the roles that have none an invitation token for the current company"""
        for rec in self.filtered(lambda role: not role.access_token):
            rec.access_token = uuid.uuid4().hex

    def _generate_qr(self, data):
        self.ensure_one()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        return base64.b64encode(temp.getvalue())

    @api.depends("access_token")
    @api.depends_context("company")
    def _compute_register_location(self):
        for rec in self:
            if not rec.access_token:
                rec.register_location = False
                rec.register_qr_code = False
                continue
            rec.register_location = "/".join(
                [
                    rec.get_base_url(),
                    self.REGISTER_ROUTE,
                    str(rec.env.company.id),
                    rec.access_token,
                ]
            )
            rec.register_qr_code = rec._generate_qr(rec.register_location)

    @api.depends("line_ids.user_id")
    def _compute_user_count(self):
        for rec in self:
            users = rec.line_ids.mapped("user_id").filtered_domain(
                [("company_ids", "=", self.env.company.id)]
            )
            rec.user_count = len(users)
            rec.user_to_verify_count = len(
                users.filtered_domain([("verified", "=", False)])
            )

    def action_user_in_role(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update({"active_test": False})
        return {
            "name": self.name,
            "res_model": "res.users",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "context": ctx,
            "domain": [
                ("company_ids", "=", self.env.company.id),
                ("role_line_ids.role_id", "=", self.id),
            ],
        }

    def action_generate_access_token(self):
        self._generate_access_token()

    def action_download_qrcode(self):
        self.ensure_one()
        self._generate_access_token()
        return {
            "type": "ir.actions.act_url",
            "url": f"/practitioner-role/{self.id}/qrcode",
            "target": "self",
        }
