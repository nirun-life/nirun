#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models


class Interpretation(models.Model):
    _name = "ni.observation.interpretation"
    _description = "Interpretation"
    _inherit = ["coding.base"]

    parent_id = fields.Many2one("ni.observation.interpretation")

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(
                _("Error! You cannot create recursive Interpretation.")
            )
