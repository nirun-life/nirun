#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class PartnerTitle(models.Model):
    _inherit = "res.partner.title"
    _order = "sequence"

    def _get_default_sequence(self):
        last_sequence = self.env[self._name].search([], order="sequence desc", limit=1)
        return last_sequence.sequence + 1 if last_sequence else 0

    sequence = fields.Integer(
        index=True, required=True, default=lambda self: self._get_default_sequence()
    )
