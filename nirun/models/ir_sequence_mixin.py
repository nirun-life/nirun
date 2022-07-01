#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models


class IrSequenceMixin(models.AbstractModel):
    _name = "ir.sequence.mixin"
    _description = "Sequence Mixin"

    _sequence_default = _("New")
    _sequence_field = "name"
    _sequence_ts_field = "period_start"

    @api.model
    def create(self, vals):
        if (
            vals.get(self._sequence_field, self._sequence_default)
            == self._sequence_default
        ):
            seq_date = fields.Date.today()
            seq = self.env["ir.sequence"]
            if self._sequence_ts_field in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals[self._sequence_ts_field])
                )
            if "company_id" in vals:
                vals[self._sequence_field] = (
                    seq.with_context(force_company=vals["company_id"]).next_by_code(
                        self._name, sequence_date=seq_date
                    )
                    or self._sequence_default
                )
            else:
                vals[self._sequence_field] = (
                    seq.next_by_code(self._name, sequence_date=seq_date)
                    or self._sequence_default
                )

        return super().create(vals)
