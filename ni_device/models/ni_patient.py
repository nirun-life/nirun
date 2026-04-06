from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    device_usage_ids = fields.One2many(
        "ni.device.usage",
        "patient_id",
        string="Device Usages",
    )

    device_usage_count = fields.Integer(
        compute="_compute_device_usage_count",
        string="Device Usage Count",
    )

    def _compute_device_usage_count(self):
        for rec in self:
            rec.device_usage_count = len(rec.device_usage_ids)
