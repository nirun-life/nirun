#  Copyright (c) 2023 NSTDA


import babel
from dateutil.relativedelta import relativedelta

from odoo import api, models
from odoo.tools import format_date, format_datetime


class DateConverter(models.AbstractModel):
    _inherit = "ir.qweb.field.date"

    @api.model
    def value_to_html(self, value, options):
        lang = self.user_lang()
        locale = babel.Locale.parse(lang.code)

        _value = value
        if str(locale) == "th_TH":
            _value = value + relativedelta(years=543)
        return format_date(self.env, _value, date_format=options.get("format"))


class DateTimeConverter(models.AbstractModel):
    _inherit = "ir.qweb.field.datetime"

    @api.model
    def value_to_html(self, value, options):
        lang = self.user_lang()
        locale = babel.Locale.parse(lang.code)

        _value = value
        if str(locale) == "th_TH":
            _value = value + relativedelta(years=543)
        return format_datetime(self.env, _value, dt_format=options.get("format"))
