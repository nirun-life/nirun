#  Copyright (c) 2021-2023 NSTDA
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "age.mixin"]
