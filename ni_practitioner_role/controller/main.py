#  Copyright (c) 2023 NSTDA

import base64

from odoo import _, fields, http
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
        return request.not_found()

    @http.route(
        "/practitioner/register/<int:company_id>/<token>/",
        type="http",
        auth="public",
        website=True,
    )
    def form_register(self, company_id, token, **kwargs):
        company = request.env["res.company"].browse(company_id)
        role = (
            request.env["res.users.role"]
            .sudo()
            .with_company(company)
            .search([("access_token", "=", token)])
        )
        if role:
            public_user = request.env.user.login == "public"
            vals = {
                "company": role.env.company,
                "role": role,
                "user": request.env.user if not public_user else None,
                "titles": request.env["res.partner.title"].search([]),
                "token": token,
                "error": kwargs.get("error"),
                "err": kwargs.get("err") or dict(),
                "post": kwargs.get("post"),
            }
            return request.render("ni_practitioner_role.register_form", vals)
        else:
            return request.not_found()

    @http.route(
        "/practitioner/register/submit", type="http", auth="public", website=True
    )
    def form_register_submit(self, **post):
        if not post or post.get("captcha"):
            return request.redirect(request.httprequest.referrer)

        comp_id = int(post.get("company_id"))
        token = post.get("token")
        login = post.get("login").strip()

        user = request.env["res.users"].sudo().search([("login", "=", login)], limit=1)
        if user:
            if not post.get("registered"):
                return self.form_register(
                    comp_id,
                    token,
                    error=_("License No. already exist"),
                    err={"login": _("License No. already exist")},
                    post=post,
                )
            else:
                user.write(
                    {
                        "role_line_ids": [
                            fields.Command.create(
                                {
                                    "role_id": int(post.get("role_id")),
                                    "date_from": fields.Date.today(),
                                    "company_id": comp_id,
                                }
                            )
                        ],
                    }
                )
                return request.render(
                    "ni_practitioner_role.register_successful",
                    {
                        "company": request.env["res.company"].browse(comp_id),
                    },
                )

        name = post.get("name").strip()
        if not name:
            return self.form_register(
                comp_id,
                token,
                error=_("Must provide patient name"),
                err={"name": _("Must provide patient name")},
                post=post,
            )

        val = self._prepare_user_value(post)
        request.env["res.users"].sudo().create(val)

        return request.render(
            "ni_practitioner_role.register_successful",
            {
                "company": request.env["res.company"].sudo().browse(comp_id),
            },
        )

    def _prepare_user_value(self, post):
        comp_id = int(post.get("company_id"))
        role_id = int(post.get("role_id"))
        return {
            "login": post.get("login").strip(),
            "password": post.get("password").strip(),
            "title": int(post.get("title_id")) if post.get("title_id") else False,
            "name": post.get("name").strip(),
            "email": post.get("email"),
            "phone": post.get("phone"),
            "mobile": post.get("mobile"),
            "company_id": comp_id,
            "verified": False,
            "company_ids": [fields.Command.link(comp_id)],
            "role_line_ids": [
                fields.Command.create(
                    {
                        "role_id": role_id,
                        "date_from": fields.Date.today(),
                        "company_id": comp_id,
                    }
                )
            ],
        }
