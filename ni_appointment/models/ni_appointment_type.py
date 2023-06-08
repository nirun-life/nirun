#  Copyright (c) 2023 NSTDA
from odoo import models


class AppointmentType(models.Model):
    _name = "ni.appointment.type"
    _description = "Appointment Type"
    _inherit = ["ni.coding"]
