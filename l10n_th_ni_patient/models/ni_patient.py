#  Copyright (c) 2021 NSTDA
import logging

from stdnum.exceptions import ValidationError as InvalidIdentificationID
from stdnum.th import pin

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Patient(models.Model):
    _inherit = "ni.patient"

    @api.model
    def default_get(self, fields):
        res = super(Patient, self).default_get(fields)
        if "nationality_id" in fields and "nationality_id" not in res:
            res["nationality_id"] = self.env.ref("base.th").id
        return res

    display_identification_id = fields.Char(
        compute="_compute_display_identification_id"
    )

    @api.onchange("identification_id")
    def _onchange_identification_id_check(self):
        if self.identification_id:
            try:
                self._check_identification_id()
            except ValidationError:
                return {
                    "warning": {
                        "title": _("Warning!"),
                        "message": _(
                            "Invalid identification number for Thailand nationality person"
                        ),
                    }
                }
            if not self._is_unique():
                return {
                    "warning": {
                        "title": _("Warning!"),
                        "message": _("Patient's identification ID must be unique!"),
                    }
                }

    def _is_unique(self):
        self.ensure_one()
        identification = self.identification_id
        if self.nationality_id.code == "TH":
            identification = pin.compact(self.identification_id)
        domain = [
            ("company_id", "=", self.company_id.id),
            ("nationality_id", "=", self.nationality_id.id),
            ("identification_id", "=", identification),
        ]
        if self.id:
            domain += ("id", "!=", self.id)
        return not bool(self.search(domain, limit=1))

    @api.depends("identification_id")
    def _compute_display_identification_id(self):
        for rec in self:
            if rec.identification_id and rec.nationality_id.code == "TH":
                rec.display_identification_id = pin.format(rec.identification_id)
            else:
                rec.display_identification_id = rec.identification_id

    @api.constrains("identification_id", "nationality_id")
    def _check_identification_id(self):
        for rec in self:
            if not rec.identification_id or rec.nationality_id.code != "TH":
                continue
            try:
                pin.validate(rec.identification_id)
                if pin.compact(rec.identification_id) != rec.identification_id:
                    _logger.debug(
                        "Compact Identification No. from {} to {}".format(
                            rec.identification_id, pin.compact(rec.identification_id)
                        )
                    )
                    rec.identification_id = pin.compact(rec.identification_id)
            except InvalidIdentificationID:
                _logger.debug(
                    "Identification No. {} [is_valid={}]".format(
                        rec.identification_id, pin.is_valid(rec.identification_id)
                    )
                )
                raise ValidationError(
                    _("Invalid identification number for Thailand nationality person")
                ) from InvalidIdentificationID
