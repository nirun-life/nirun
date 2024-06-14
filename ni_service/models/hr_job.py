#  Copyright (c) 2024 NSTDA
import random

from odoo import fields, models


class HrJob(models.Model):
    _inherit = "hr.job"

    color = fields.Integer(default=lambda _: random.randint(0, 10))
