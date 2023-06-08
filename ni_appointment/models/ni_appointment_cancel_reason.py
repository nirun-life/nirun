#  Copyright (c) 2023 NSTDA
from odoo import models


class AppointmentCancelReason(models.Model):
    _name = "ni.appointment.cancel.reason"
    _description = "Appointment Cancellation Reason"
    _inherit = ["ni.coding"]
