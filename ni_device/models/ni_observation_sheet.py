from odoo import models


class ObservationSheet(models.Model):
    _name = "ni.observation.sheet"
    _inherit = ["ni.observation.sheet", "ni.device.usage.log.mixin"]
