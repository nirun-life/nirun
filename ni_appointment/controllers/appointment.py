# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
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

    @http.route(["/my/appointment"], type="http", auth="user", website=True)
    def portal_my_appointment(self, **kw):
        values = self._prepare_portal_layout_values()
        Appointment = request.env["ni.appointment"]
        domain = [("partner_ids", "=", request.env.user.partner_id.id)]

        appointments = Appointment.search(domain)

        values.update(
            {
                "appointments": appointments,
                "page_name": "appointment",
                "default_url": "/my/appointment",
            }
        )

        return request.render("ni_appointment.portal_my_appointments", values)

    @http.route(
        ["/my/appointment/<int:appointment_id>"], type="http", auth="user", website=True
    )
    def portal_my_project(
        self,
        appointment_id=None,
        access_token=None,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        search=None,
        search_in="content",
        groupby=None,
        task_id=None,
        **kw
    ):
        values = self._prepare_portal_layout_values()
        Appointment = request.env["ni.appointment"]
        domain = [("id", "=", int(appointment_id))]

        appointments = Appointment.search(domain)
        values.update(
            {
                "task": appointments[0],
                "page_name": "appointment",
                "default_url": "/my/appointment",
            }
        )
        return request.render("ni_appointment.portal_my_appointment", values)
