#  Copyright (c) 2023 NSTDA
""" mail_render_mixin.py

   isort:skip_file
"""

import copy

import babel
from dateutil.relativedelta import relativedelta

from odoo import api, tools
from odoo.tools import get_lang, is_html_empty

from odoo.addons.mail.models.mail_render_mixin import (
    MailRenderMixin,
    format_time,
    template_env_globals,
)


def format_date(env, date, pattern=False, lang_code=False):
    try:
        lang = get_lang(env, lang_code)
        locale = babel.Locale.parse(
            lang.code or lang_code
        )  # lang can be inactive, so `lang`is empty
        _date = date
        if str(locale) == "th_TH":
            _date = date + relativedelta(years=543)
        return tools.format_date(env, _date, date_format=pattern, lang_code=lang_code)
    except babel.core.UnknownLocaleError:
        return date


def format_datetime(env, dt, tz=False, dt_format="medium", lang_code=False):
    try:
        lang = get_lang(env, lang_code)
        locale = babel.Locale.parse(
            lang.code or lang_code
        )  # lang can be inactive, so `lang`is empty
        _dt = dt
        if str(locale) == "th_TH":
            _dt = dt + relativedelta(years=543)
        return tools.format_datetime(
            env, _dt, tz=tz, dt_format=dt_format, lang_code=lang_code
        )
    except babel.core.UnknownLocaleError:
        return dt


@api.model
def _render_eval_context(self):
    """
    Override format_date and formate_datetime
    """
    render_context = {
        "format_date": lambda date, date_format=False, lang_code=False: format_date(
            self.env, date, date_format, lang_code
        ),
        "format_datetime": lambda dt, tz=False, dt_format=False, lang_code=False: format_datetime(
            self.env, dt, tz, dt_format, lang_code
        ),
        "format_time": lambda time, tz=False, time_format=False, lang_code=False: format_time(
            self.env, time, tz, time_format, lang_code
        ),
        "format_amount": lambda amount, currency, lang_code=False: tools.format_amount(
            self.env, amount, currency, lang_code
        ),
        "format_duration": lambda value: tools.format_duration(value),
        "user": self.env.user,
        "ctx": self._context,
        "is_html_empty": is_html_empty,
    }
    render_context.update(copy.copy(template_env_globals))
    return render_context


MailRenderMixin._render_eval_context = _render_eval_context
