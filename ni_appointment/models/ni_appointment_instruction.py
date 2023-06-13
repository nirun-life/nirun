#  Copyright (c) 2023 NSTDA
from odoo import models


class AppointmentType(models.Model):
    _name = "ni.appointment.instruction"
    _description = "Appointment Patient Instruction"
    _inherit = ["ni.coding"]
