#  Copyright (c) 2021 Piruin P.

from odoo import models


class Partner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        if self._context.get("show_address") == 2:
            result = []
            for partner in self:
                name = partner.contact_address.replace("\n", " ").strip()
                if partner.name:
                    name = "\n".join((partner.name, name))
                result.append((partner.id, name))
            return result
        return super(Partner, self).name_get()
