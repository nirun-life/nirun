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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (
                vals.get(self._identifier_field, self._identifier_default)
                == self._identifier_default
                or self._identifier_field not in vals
            ):
                seq_date = fields.Date.today()
                if self._identifier_ts_field in vals:
                    seq_date = fields.Datetime.context_timestamp(
                        self,
                        fields.Datetime.to_datetime(vals[self._identifier_ts_field]),
                    )
                seq = self.env["ir.sequence"]
                if "company_id" in vals:
                    vals[self._identifier_field] = (
                        seq.with_context(with_company=vals["company_id"]).next_by_code(
                            self._name, sequence_date=seq_date
                        )
                        or self._identifier_default
                    )
                else:
                    vals[self._identifier_field] = (
                        seq.next_by_code(self._name, sequence_date=seq_date)
                        or self._identifier_default
                    )
        return super().create(vals_list)
