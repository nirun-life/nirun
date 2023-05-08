#  Copyright (c) 2023 NSTDA

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tools import get_lang

from odoo.addons.mail.models.mail_tracking_value import MailTracking


def _get_display_value(self, prefix):
    assert prefix in ("new", "old")
    result = []
    lang = get_lang(self.env)
    for record in self:
        if record.field_type in ["integer", "float", "char", "text", "monetary"]:
            result.append(record[f"{prefix}_value_{record.field_type}"])
        elif record.field_type == "datetime":
            if record[f"{prefix}_value_datetime"]:
                # override
                new_datetime = record[f"{prefix}_value_datetime"]
                if lang.code == "th_TH":
                    new_datetime = new_datetime + relativedelta(years=543)
                result.append(f"{new_datetime}Z")
            else:
                result.append(record[f"{prefix}_value_datetime"])
        elif record.field_type == "date":
            if record[f"{prefix}_value_datetime"]:
                # override
                new_date = record[f"{prefix}_value_datetime"]
                if lang.code == "th_TH":
                    new_date = new_date + relativedelta(years=543)
                result.append(fields.Date.to_string(new_date))
            else:
                result.append(record[f"{prefix}_value_datetime"])
        elif record.field_type == "boolean":
            result.append(bool(record[f"{prefix}_value_integer"]))
        else:
            result.append(record[f"{prefix}_value_char"])
    return result


MailTracking._get_display_value = _get_display_value
