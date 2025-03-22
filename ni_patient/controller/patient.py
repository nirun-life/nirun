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

    @http.route(["/my/patients"], type="http", auth="user", website=True)
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
                "default_url": "/my/patients",
            }
        )
        # print("PatientPortal Values:", values)  # Debug

        return request.render("ni_patient.portal_my_patients", values)

    @http.route(
        ["/my/patients/<int:patient_id>"], type="http", auth="user", website=True
    )
    def portal_my_patient(self, patient_id=None, **kw):
        values = self._prepare_portal_layout_values()
        Encounters = request.env["ni.encounter"]
        domain = [("patient_id", "=", int(patient_id))]

        encounters = Encounters.search(domain, limit=self._items_per_page)
        values.update(
            {
                "patient": encounters.patient_id,
                "encounters": encounters,
                "page_name": "encounters",
                "default_url": "/my/patients",
                "user": request.env.user,
            }
        )

        # print("portal_my_patient Values:", values)  # Debug
        return request.render("ni_patient.portal_my_patient", values)

    @http.route(
        ["/my/patients/<int:patient_id>/<int:encounter_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_patient_encounter(self, encounter_id=None, **kw):
        values = self._prepare_portal_layout_values()
        Encounters = request.env["ni.encounter"]
        domain = [("id", "=", int(encounter_id))]

        encounters = Encounters.search(domain)
        values.update(
            {
                "encounter": encounters[0],
                "page_name": "encounter",
                "default_url": "/my/patients",
                "user": request.env.user,
            }
        )

        # print("portal_my_patient_encounter Values:", values)  # Debug
        return request.render("ni_patient.portal_my_patient_encounter", values)
