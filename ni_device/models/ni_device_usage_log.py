from odoo import fields, models


class DeviceUsageLog(models.Model):
    _name = "ni.device.usage.log"
    _inherit = "ni.observation.vitalsign.mixin", "image.mixin"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    device_id = fields.Many2one(
        "ni.device", required=True, index=True, ondelete="cascade"
    )

    user_id = fields.Many2one(
        "res.users", "ผู้อ่านบัตร", required=True, default=lambda self: self.env.user
    )
    patient_id = fields.Many2one("ni.patient", copy=False)
