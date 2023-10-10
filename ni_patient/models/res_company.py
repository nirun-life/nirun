#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    encounter_class_id = fields.Many2one("ni.encounter.class")
