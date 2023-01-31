#  Copyright (c) 2023. NSTDA
from odoo import fields, models


class Goal(models.Model):
    _inherit = "ni.goal"

    state = fields.Selection(selection_add=[("replaced", "Replaced")])

    def action_replace(self):
        self.filtered_domain([("state", "in", ["proposed", "active"])]).write(
            {"state": "replaced"}
        )
