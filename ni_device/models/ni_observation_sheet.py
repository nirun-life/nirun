from odoo import fields, models


class ObservationSheet(models.Model):
    _name = "ni.observation.sheet"
    _inherit = ["ni.observation.sheet", "ni.device.usage.log.mixin"]

    device_id = fields.Many2one("ni.device", index=True, ondelete="restrict")
