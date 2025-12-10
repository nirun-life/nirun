from odoo import fields, models


class DeviceHolder(models.Model):
    _name = "ni.device.holder"
    _description = "Device Holder History"
    _order = "create_date DESC"
    _inherit = "ni.holder.mixin"

    device_id = fields.Many2one("ni.device", string="Device", required=True)
    device_identifier = fields.Char(
        related="device_id.identifier", string="Device Identifier"
    )

    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date")

    request_id = fields.Many2one("ni.device.request", string="Related Request")
