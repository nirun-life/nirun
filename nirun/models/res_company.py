#  Copyright (c) 2021 NSTDA

import base64

from odoo import api, models
from odoo.modules.module import get_module_resource


class Company(models.Model):
    _inherit = "res.company"

    @api.model
    def _get_default_favicon(self, original=False):
        image_path = get_module_resource("nirun", "static/src/img", "favicon.ico")
        return base64.b64encode(open(image_path, "rb").read())
