#  Copyright (c) 2023-2023. NSTDA

from odoo import fields, models


class Condition(models.Model):
    _inherit = "ni.condition"

    diagnosis_id = fields.One2many("ni.encounter.diagnosis", "condition_id")
