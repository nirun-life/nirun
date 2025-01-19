#  Copyright (c) 2024. NSTDA

from odoo import api, models


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
        ir.rule domains.
        Note: company_ids contains the ids of the activated companies
        by the user with the switch company menu. These companies are
        filtered and trusted.
        """
        # use an empty context for 'user' to make the domain evaluation
        # independent from the context
        vals = super(IrRule, self)._eval_context()
        vals["city_ids"] = self.env.user.city_ids.ids
        return vals
