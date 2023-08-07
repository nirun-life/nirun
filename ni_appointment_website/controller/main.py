#  Copyright (c) 2023 NSTDA
import json

from pytz import timezone, utc
from werkzeug import exceptions

import odoo.http as http
from odoo import _, fields
from odoo.http import request
from odoo.tools.date_utils import relativedelta


def _prepare_appointment_time(post):
    tz = timezone(request.env.user.tz or "UTC")
    start = tz.localize(
        fields.Datetime.to_datetime(
            "%s %s" % (post.get("start"), post.get("start_time"))
        )
    )
    if start.minute not in [0, 30]:
        m = start.minute
        if m > 30:
            m = m - 30
        start = start - relativedelta(minutes=m)
    stop = start + relativedelta(minutes=30)
    return start.astimezone(utc), stop.astimezone(utc)


class AppointmentController(http.Controller):
    def _query_company(self, q):
        query = []
        if len(q.split()) > 1:
            q_zip = None
            for n in q.split():
                if n.isnumeric and len(n) == 5:
                    q_zip = n
                    continue
                query.append(("name", "ilike", n))
            if q_zip:
                query.append(("zip", "=", q_zip))
        else:
            query += ["|", ("name", "ilike", q), ("partner_id.zip", "ilike", q)]
        return query

    @http.route("/appointment", type="http", auth="public", website=True)
    def appointment_index_page(self, q=None, page=1, limit=10, **kwargs):
        res_company = request.env["res.company"].sudo()

        count = res_company.search_count([])
        if count == 1:
            c = res_company.search([], limit=1)
            return request.redirect("/appointment/form?company_id=%s" % c.id)

        vals = {"q": q, "page": page}
        if q:
            query = self._query_company(q)
            company_ids = res_company.search(
                query, offset=(page - 1) * limit, limit=limit
            )
            count = res_company.search(query, count=True)
            vals.update({"company_ids": company_ids, "q_count": count})

        return request.render("ni_appointment_website.company_search", vals)

    @http.route("/appointment/form", type="http", auth="user", website=True)
    def appointment_make(self, company_id, **kwargs):
        if not company_id:
            return request.redirect("/appointment")

        comp_id = int(company_id)
        company = request.env["res.company"].sudo().browse(comp_id)[0]
        depart = (
            request.env["hr.department"].sudo().search([("company_id", "=", comp_id)])
        )
        employee_no_depart = (
            request.env["hr.employee.public"]
            .sudo()
            .search([("company_id", "=", comp_id), ("department_id", "=", False)])
        )
        today = fields.date.today()

        vals = {
            "user": request.env.user,
            "company": company,
            "department_ids": depart,
            "employee_ids": employee_no_depart,
            "date_min": today,
            "date_max": today + relativedelta(years=1),
            "error": kwargs.get("error"),
        }
        return request.render("ni_appointment_website.appointment_form", vals)

    @http.route(
        "/appointment/submit", type="http", auth="user", website=True, sitemap=False
    )
    def appointment_submit(self, **post):
        if not post or post.get("captcha"):
            return request.redirect("/appointment")

        comp_id = int(post.get("company_id"))
        patient_name = post.get("patient_name").strip()

        if not patient_name:
            return self.appointment_make(comp_id, error="Must provide patient name")
        if len(patient_name.split()) != 2:
            return self.appointment_make(
                comp_id, error="Patient name must be in format 'Fistname Lastname'"
            )

        partner_id = request.env.user.partner_id.id
        if request.env.user.name == patient_name:
            # If this appointment make for user themselves
            pat_search = [
                ("company_id", "=", comp_id),
                ("partner_id", "=", partner_id),
            ]
            patient = request.env["ni.patient"].sudo().search(pat_search, limit=1)
            if not patient:
                # We can auto-register patient into system if user not already registered
                patient = self._regis_patient(comp_id, partner_id, post)
        else:
            # When appointment made by patient's caregiver we try to search registered patient as best as we can,
            # TODO We shouldn't auto-register! because it may lead to create duplicate record
            pat_search = [
                ("company_id", "=", comp_id),
                ("name", "ilike", patient_name),
            ]
            pat_search = self._tel_search_param(pat_search, post)
            patient = request.env["ni.patient"].sudo().search(pat_search, order="id")
            if not patient:
                partner_search = [("name", "=", patient_name)]
                partner_search = self._tel_search_param(partner_search, post)
                partner = request.env["res.partner"].sudo().search(partner_search)
                if not partner:
                    partner_vals = {
                        "name": patient_name,
                        "phone": post.get("patient_phone"),
                        "mobile": post.get("patient_mobile"),
                        "email": post.get("patient_email"),
                    }
                    partner = request.env["res.partner"].sudo().create(partner_vals)
                patient = self._regis_patient(comp_id, partner[0].id, post)

        start, stop = _prepare_appointment_time(post)
        performer_id = None
        if post.get("practitioner_id"):
            performer_id = int(post.get("practitioner_id"))

        vals = {
            "name": _("Self Appointment"),
            "patient_id": patient.id,
            "performer_id": performer_id,
            "start": start.strftime("%Y-%m-%d %H:%M:%S"),
            "stop": stop.strftime("%Y-%m-%d %H:%M:%S"),
            "description": post.get("description"),
            "user_id": request.env.user.id,
        }
        appoint = request.env["ni.appointment"].sudo().create(vals)
        if appoint.patient_id:
            appoint.action_active()
            appoint.write({"state": "draft"})
        return request.redirect("/my/appointment/%s" % appoint.id)

    def _regis_patient(self, comp_id, partner_id, post):
        patient_vals = {
            "company_id": comp_id,
            "partner_id": partner_id,
            "phone": post.get("patient_phone"),
            "mobile": post.get("patient_mobile"),
            "email": post.get("patient_email"),
        }
        return request.env["ni.patient"].sudo().create(patient_vals)[0]

    def _tel_search_param(self, search, post):
        if post.get("patient_mobile") or post.get("patient_phone"):
            # Use mobile&phone to improve search accuracy
            tel = []
            if post.get("patient_mobile"):
                tel.append(post["patient_mobile"].strip())
            if post.get("patient_phone"):
                tel.append(post["patient_phone"].strip())
            if tel:
                search = search + ["|", ("mobile", "in", tel), ("phone", "in", tel)]
        return search

    @http.route("/appointment/check", auth="public")
    def appointment_check(self, performer_id, start_date, start_time):
        tz = timezone(request.env.user.tz or "UTC")
        try:
            dt = fields.Datetime.to_datetime("%s %s" % (start_date, start_time))
            start = tz.localize(dt)
        except ValueError:
            return exceptions.BadRequest("Invalid Datetime format")

        emp = request.env["hr.employee"].browse(int(performer_id))
        return json.dumps({"count": self._get_appointment_count(emp, start)})

    def _get_appointment_count(self, emp, start):
        if start.minute not in [0, 30]:
            m = start.minute
            if m > 30:
                m = m - 30
            start = start - relativedelta(minutes=m)
        stop = start + relativedelta(minutes=30)
        return request.env["ni.appointment"].search_count(
            [
                ("performer_id", "=", emp.id),
                ("state", "in", ["draft", "active"]),
                ("start", "<", stop.astimezone(utc)),
                ("stop", ">", start.astimezone(utc)),
            ]
        )
