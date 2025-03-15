# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class PatientPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "patient_count" in counters:
            values["patient_count"] = (
                request.env["ni.patient"].search_count(
                    [("user_ids", "=", request.env.user.id)]
                )
                if request.env["ni.patient"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )

        # print("PatientPortal Values:", values)  # Debug

        return values

    @http.route(["/my/patient"], type="http", auth="user", website=True)
    def portal_my_patients(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        Patient = request.env["ni.patient"]
        domain = [("user_ids", "=", request.env.user.id)]

        patients = Patient.search(domain, limit=self._items_per_page)
        values.update(
            {
                "patients": patients,
                "page_name": "patient",
                "default_url": "/my/patient",
            }
        )
        # print("PatientPortal Values:", values)  # Debug

        return request.render("ni_patient_website.portal_my_patients", values)

    # @http.route(
    #     ["/my/appointment/<int:appointment_id>"], type="http", auth="user", website=True
    # )
    # def portal_my_appointment(self, appointment_id=None, **kw):
    #     values = self._prepare_portal_layout_values()
    #     Appointment = request.env["ni.appointment"]
    #     domain = [("id", "=", int(appointment_id))]
    #
    #     appointments = Appointment.search(domain)
    #     reason = request.env["ni.appointment.cancel.reason"].search([])
    #     values.update(
    #         {
    #             "appointment": appointments[0],
    #             "page_name": "appointment",
    #             "default_url": "/my/appointment",
    #             "reason": reason,
    #             "user": request.env.user,
    #             "tz": pytz.timezone(request.env.user.tz),
    #         }
    #     )
    #     history = "my_appointment_history"
    #     values = self._get_page_view_values(
    #         appointments[0], None, values, history, False, **kw
    #     )
    #     return request.render("ni_appointment.portal_my_appointment", values)
    #
