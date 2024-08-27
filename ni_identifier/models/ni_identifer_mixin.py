#  Copyright (c) 2023 NSTDA

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


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
                self._identifier_field not in vals
                or (
                    vals.get(self._identifier_field, self._identifier_default)
                    or self._identifier_default
                )
                == self._identifier_default
            ):
                seq_date = fields.Date.today()
                if self._identifier_ts_field in vals:
                    seq_date = fields.Datetime.context_timestamp(
                        self,
                        fields.Datetime.to_datetime(vals[self._identifier_ts_field]),
                    )
                seq = self.env["ir.sequence"]
                if "company_id" in vals:
                    seq = seq.with_context(with_company=vals["company_id"])
                vals[self._identifier_field] = seq.next_by_code(self._name, seq_date)
                if not vals[self._identifier_field]:
                    vals[self._identifier_field] = self._identifier_default
                    _logger.warning(
                        "Not found ir.sequence code={}, used default '{}' instead".format(
                            self._name, self._identifier_default
                        )
                    )

        return super().create(vals_list)
