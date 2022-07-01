#  Copyright (c) 2021 NSTDA

from odoo import _, api, models


class Patient(models.Model):
    _inherit = "ni.patient"

    @api.onchange("name")
    def _onchange_name(self):
        if self.name and self._search_duplicate_name():
            return {
                "warning": {
                    "title": _("Warning! name already exist"),
                    "message": _(
                        "Patient with name [%s] was already registered.\n\n"
                        "Please review there is not the same person."
                    )
                    % (self.name),
                }
            }

    def _search_duplicate_name(self):
        self.ensure_one()
        domain = [("company_id", "=", self.company_id.id), ("name", "=", self.name)]
        if self.id:
            domain.append(("id", "!=", self.id[0]))
        return self.env["ni.patient"].search(domain)
