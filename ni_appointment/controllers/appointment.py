# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class AppointmentPortal(CustomerPortal):
    @http.route(["/my/appointment"], type="http", auth="public", website=True)
    def portal_my_appointment(self):

        return request.render("ni_appointment.portal_my_appointments", {})
