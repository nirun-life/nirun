#  Copyright (c) 2021 Piruin P.

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Patient(models.Model):
    _inherit = "ni.patient"

    nationality_id = fields.Many2one(
        default=lambda self: self.env.ref("base.th"),
    )

    _sql_constraints = [
        (
            "identification_id_unique",
            "unique (company_id, nationality_id, identification_id)",
            _("This Identification No. was already exist"),
        ),
    ]

    @api.onchange("identification_id", "nationality_id")
    def _preprocess_identification_id(self):
        if "TH" == self.nationality_id.code and self.identification_id:
            self.identification_id = re.sub("\\D", "", self.identification_id)

    @api.constrains("identification_id", "nationality_id")
    def _check_identification_id(self):
        for record in self:
            if "TH" == record.nationality_id.code and record.identification_id:
                _id = record.identification_id
                if len(_id) != 13 or not _id.isdigit():
                    raise UserError(
                        _("Identification No of Thai citizen must be 13 digits")
                    )
                x = sum([(13 - i) * int(_id[i]) for i in range(12)]) % 11
                checksum = (11 - x) % 10
                if int(_id[12]) != checksum:
                    raise UserError(_("Invalid Thai Identification Id"))
