#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class Company(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "ni.identifier.mixin"]
    _rec_name = "name"
    _rec_names_search = "name,identifier,vat"

    encounter_class_id = fields.Many2one(
        "ni.encounter.class", help="Default encounter class of this company"
    )
