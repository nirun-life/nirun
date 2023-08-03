# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pytz

from odoo import _, http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class AppointmentPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "appointment_count" in counters:
            values["appointment_count"] = (
                request.env["ni.appointment"].search_count(
                    [("partner_ids", "=", request.env.user.partner_id.id)]
                )
                if request.env["ni.appointment"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
        return values

    def _prepare_searchbar_sortings(self):
        return {
            "date": {"label": _("Newest"), "order": "start desc"},
            "name": {"label": _("Name"), "order": "name"},
            "performer": {"label": _("Performer"), "order": "performer_id, start desc"},
            "company": {"label": _("Company"), "order": "company_id, start desc"},
        }

    @http.route(["/my/appointment"], type="http", auth="user", website=True)
    def portal_my_appointments(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        Appointment = request.env["ni.appointment"]
        domain = [("partner_ids", "=", request.env.user.partner_id.id)]

        searchbar_sortings = self._prepare_searchbar_sortings()
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        appointments = Appointment.search(
            domain, order=order, limit=self._items_per_page
        )

        values.update(
            {
                "appointments": appointments,
                "page_name": "appointment",
                "default_url": "/my/appointment",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )

        return request.render("ni_appointment.portal_my_appointments", values)

    @http.route(
        ["/my/appointment/<int:appointment_id>"], type="http", auth="user", website=True
    )
    def portal_my_appointment(self, appointment_id=None):
        values = self._prepare_portal_layout_values()
        Appointment = request.env["ni.appointment"]
        domain = [("id", "=", int(appointment_id))]

        appointments = Appointment.search(domain)
        reason = request.env["ni.appointment.cancel.reason"].search([])
        values.update(
            {
                "appointment": appointments[0],
                "page_name": "appointment",
                "default_url": "/my/appointment",
                "reason": reason,
                "user": request.env.user,
                "tz": pytz.timezone(request.env.user.tz),
            }
        )
        return request.render("ni_appointment.portal_my_appointment", values)

    @http.route(
        "/appointment/cancel", type="http", auth="user", website=True, sitemap=False
    )
    def appointment_submit(self, **post):
        if not post or post.get("captcha"):
            return request.redirect("/my/appointment")

        appointment_id = int(post.get("appointment_id"))
        reason_id = int(post.get("reason_id"))
        reason_detail = post.get("reason_detail").strip()
        appoint = request.env["ni.appointment"].sudo().browse(appointment_id)
        appoint.write(
            {
                "cancel_reason_id": reason_id,
                "cancel_note": reason_detail,
                "state": "revoked",
            }
        )

        return request.redirect("/my/appointment/%s" % appointment_id)
