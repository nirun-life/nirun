from odoo import fields, models


class DeviceLabelLayout(models.TransientModel):
    _name = "ni.device.label.layout"
    _description = "Device Label Layout"

    device_id = fields.Many2one("ni.device", required=True, readonly=True)
    quantity = fields.Integer(
        string="Quantity",
        default=1,
        required=True,
    )

    def action_print(self):
        self.ensure_one()
        return self.env.ref("ni_device.action_report_device_label").report_action(
            self.device_id,
            data={
                "quantity": self.quantity,
            },
        )
