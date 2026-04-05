from odoo import models


class PatientSmartcard(models.Model):
    _name = "ni.patient.smartcard"
    _inherit = ["ni.patient.smartcard", "ni.device.usage.log.mixin"]
