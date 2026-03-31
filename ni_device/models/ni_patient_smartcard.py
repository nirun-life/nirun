from odoo import fields, models


class PatientSmartcard(models.Model):
    _name = "ni.patient.smartcard"
    _inherit = ["ni.patient.smartcard", "ni.device.usage.log.mixin"]

    device_id = fields.Many2one("ni.device", index=True)
