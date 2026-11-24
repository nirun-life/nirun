#  Copyright (c) 2023 NSTDA

import base64

from odoo import fields, http
from odoo.http import request


class PractitionerRoleController(http.Controller):
    @http.route("/practitioner-role/<int:role_id>/qrcode", type="http", auth="user")
    def get_qrcode(self, role_id, **kw):
        role = request.env["res.users.role"].browse(role_id)
        if role:
            if role.register_qr_code:
                file_data = base64.b64decode(role.register_qr_code)
                return request.make_response(
                    file_data,
                    [
                        ("Content-Type", "application/octet-stream"),
                        (
                            "Content-Disposition",
                            f"attachment; filename={role.name}.png",
                        ),
                    ],
                )
        raise request.not_found()

    @http.route(
        "/practitioner/register/<int:company_id>/<token>",
        type="http",
        auth="public",
        website=True,
    )
    def form_register(self, company_id, token, **kwargs):
        role = self._get_role(company_id, token)
        return self._render_register_form(role, token)

    @http.route(
        "/practitioner/register/submit",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def form_register_submit(self, **post):
        if post.get("captcha"):
            return request.redirect(request.httprequest.referrer or "/")

        # The invitation decides the company and the role, never the posted values
        token = post.get("token")
        role = self._get_role(post.get("company_id"), token)
        company = role.env.company
        if not request.env.user._is_public():
            return self._register_current_user(role, token)

        login = (post.get("login") or "").strip()
        name = (post.get("name") or "").strip()
        err = {}
        if not login:
            err["login"] = request.env._("Must provide license no.")
        elif request.env["res.users"].sudo().search([("login", "=", login)], limit=1):
            err["login"] = request.env._("License No. already exist")
        elif not (post.get("password") or "").strip():
            err["password"] = request.env._("Must provide password")
        elif not name:
            err["name"] = request.env._("Must provide practitioner name")
        if err:
            error = next(iter(err.values()))
            return self._render_register_form(role, token, error, err, post)

        request.env["res.users"].sudo().create(self._prepare_user_value(post, role))
        return self._render_successful(company)

    def _get_role(self, company_id, token):
        """Role (in the company of the invitation) that a token gives access to"""
        try:
            company = request.env["res.company"].sudo().browse(int(company_id)).exists()
        except (TypeError, ValueError):
            company = request.env["res.company"]
        # An empty token would match the roles that have none
        if not company or not token:
            raise request.not_found()
        role = (
            request.env["res.users.role"]
            .sudo()
            .with_company(company)
            .search([("access_token", "=", token)], limit=1)
        )
        if not role:
            raise request.not_found()
        return role

    def _register_current_user(self, role, token):
        """Add the role to the signed in user, whatever login was posted"""
        user = request.env.user
        company = role.env.company
        if company not in user.company_ids:
            error = request.env._("You do not have access to this company")
            return self._render_register_form(role, token, error)
        vals = self._prepare_role_line_value(role.id, company.id)
        lines = user.sudo().role_line_ids.filtered(lambda line: line.role_id == role)
        if "company_id" in vals:
            lines = lines.filtered(
                lambda line: not line.company_id or line.company_id == company
            )
        if not lines:
            user.sudo().write({"role_line_ids": [fields.Command.create(vals)]})
        return self._render_successful(company)

    def _render_register_form(self, role, token, error=None, err=None, post=None):
        user = request.env.user
        return request.render(
            "ni_practitioner_role.register_form",
            {
                "company": role.env.company,
                "role": role,
                "user": None if user._is_public() else user,
                "titles": request.env["res.partner.title"].sudo().search([]),
                "token": token,
                "error": error,
                "err": err or {},
                "post": post,
            },
        )

    def _render_successful(self, company):
        return request.render(
            "ni_practitioner_role.register_successful", {"company": company.sudo()}
        )

    def _prepare_user_value(self, post, role):
        company = role.env.company
        return {
            "login": post.get("login").strip(),
            "password": post.get("password").strip(),
            "title_id": int(post.get("title")) if post.get("title") else False,
            "name": post.get("name").strip(),
            "email": post.get("email"),
            "phone": post.get("phone"),
            "mobile": post.get("mobile"),
            "company_id": company.id,
            "verified": False,
            "company_ids": [fields.Command.link(company.id)],
            "role_line_ids": [
                fields.Command.create(
                    self._prepare_role_line_value(role.id, company.id)
                )
            ],
        }

    def _prepare_role_line_value(self, role_id, company_id):
        vals = {"role_id": role_id, "date_from": fields.Date.today()}
        # Only with base_user_role_company, which is AGPL-3 and so not a dependency
        if "company_id" in request.env["res.users.role.line"]._fields:
            vals["company_id"] = company_id
        return vals
