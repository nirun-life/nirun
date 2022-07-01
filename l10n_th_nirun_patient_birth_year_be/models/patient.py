#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    birth_year_be = fields.Integer(
        "Year of Birth (BE)",
        compute="_compute_birth_year_be",
        inverse="_inverse_birth_year_be",
        store=True,
        default=None,
    )

    @api.onchange("birthdate")
    def _onchange_birthdate(self):
        if self.birthdate and self.birth_year_be != (self.birthdate.year + 543):
            self.birth_year_be = self.birthdate.year + 543

    @api.depends("birthdate")
    def _compute_birth_year_be(self):
        for rec in self:
            rec._onchange_birthdate()

    @api.onchange("birth_year_be")
    def _onchange_birth_year_be(self):
        if self.birth_year_be and (
            not self.birthdate or self.birthdate.year != self.birth_year_be - 543
        ):
            if self.birth_year_be < 1900 + 543:
                return {
                    "warning": {
                        "title": _("Error"),
                        "message": _("System does not support date before 1900-01-01"),
                    },
                    "value": {"birth_year_be": 1900 + 543},
                }
            self._inverse_birth_year_be()

    def _inverse_birth_year_be(self):
        today = fields.date.today().replace(month=1, day=1)
        for rec in self:
            if not rec.birth_year_be:
                continue
            base = rec.birthdate or today
            date = "{}-{}-{}".format(rec.birth_year_be - 543, base.month, base.day)
            rec.birthdate = fields.Date.to_date(date)
