#  Copyright (c) 2021 Piruin P.

from odoo import api, models


class Patient(models.Model):
    _inherit = "ni.patient"

    @api.onchange("title", "firstname", "lastname")
    def _compute_name(self):
        """This function require because partner._get_computed_name() doesn't
        get title value when onchange was called"""
        for rec in self:
            rec.name = " ".join(
                p for p in (rec.title.name, rec.firstname, rec.lastname) if p
            )
