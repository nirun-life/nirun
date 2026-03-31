from odoo import fields, models


class DeviceHolder(models.Model):
    _name = "ni.device.holder"
    _description = "Device Holder History"
    _order = "create_date DESC"
    _inherit = "ni.holder.mixin"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_id = fields.Many2one(
        "ni.device",
        string="Device",
        check_company=True,
        index=True,
        required=True,
        ondelete="cascade",
    )
    device_identifier = fields.Char(
        related="device_id.identifier", string="Device Identifier"
    )
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date")

    request_id = fields.Many2one("ni.device.request", string="Related Request")
