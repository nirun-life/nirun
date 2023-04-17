#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models


class IdentifierMixin(models.AbstractModel):
    _name = "ni.identifier.mixin"
    _description = "Record Identifier Mixin"
    _rec_name = "identifier"

    _identifier_default = _("New")
    _identifier_field = "identifier"
    _identifier_ts_field = "period_start"

    identifier = fields.Char(default=_identifier_default)

    @api.model
    def create(self, vals):
        if (
            vals.get(self._identifier_field, self._identifier_default)
            == self._identifier_default
        ):
            seq_date = fields.Date.today()
            seq = self.env["ir.sequence"]
            if self._identifier_ts_field in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals[self._identifier_ts_field])
                )
            if "company_id" in vals:
                vals[self._identifier_field] = (
                    seq.with_context(force_company=vals["company_id"]).next_by_code(
                        self._name, sequence_date=seq_date
                    )
                    or self._identifier_default
                )
            else:
                vals[self._identifier_field] = (
                    seq.next_by_code(self._name, sequence_date=seq_date)
                    or self._identifier_default
                )
        return super().create(vals)
