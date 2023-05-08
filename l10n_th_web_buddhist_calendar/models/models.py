#  Copyright (c) 2023 NSTDA

import babel
import pytz
from dateutil.relativedelta import relativedelta

from odoo import api
from odoo.models import BaseModel
from odoo.osv import expression
from odoo.tools import get_lang
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


@api.model
def _read_group_format_result(self, data, annotated_groupbys, groupby, domain):
    """
        Helper method to format the data contained in the dictionary data by
        adding the domain corresponding to its values, the groupbys in the
        context and by properly formatting the date/datetime values.

    :param data: a single group
    :param annotated_groupbys: expanded grouping metainformation
    :param groupby: original grouping metainformation
    :param domain: original domain for read_group
    """

    sections = []
    for gb in annotated_groupbys:
        ftype = gb["type"]
        value = data[gb["groupby"]]

        # full domain for this groupby spec
        d = None
        if value:
            if ftype in ["many2one", "many2many"]:
                value = value[0]
            elif ftype in ("date", "datetime"):
                locale = get_lang(self.env).code
                fmt = (
                    DEFAULT_SERVER_DATETIME_FORMAT
                    if ftype == "datetime"
                    else DEFAULT_SERVER_DATE_FORMAT
                )
                tzinfo = None
                range_start = value
                range_end = value + gb["interval"]
                # value from postgres is in local tz (so range is
                # considered in local tz e.g. "day" is [00:00, 00:00[
                # local rather than UTC which could be [11:00, 11:00]
                # local) but domain and raw value should be in UTC
                if gb["tz_convert"]:
                    tzinfo = range_start.tzinfo
                    range_start = range_start.astimezone(pytz.utc)
                    # take into account possible hour change between start and end
                    range_end = tzinfo.localize(range_end.replace(tzinfo=None))
                    range_end = range_end.astimezone(pytz.utc)

                range_start = range_start.strftime(fmt)
                range_end = range_end.strftime(fmt)

                # =============================================================
                # Override start
                _value = value
                if locale == "th_TH":
                    _value = value + relativedelta(years=543)

                if ftype == "datetime":
                    label = babel.dates.format_datetime(
                        _value,
                        format=gb["display_format"],
                        tzinfo=tzinfo,
                        locale=locale,
                    )
                else:
                    label = babel.dates.format_date(
                        _value, format=gb["display_format"], locale=locale
                    )
                # Override end
                # =============================================================

                data[gb["groupby"]] = ("%s/%s" % (range_start, range_end), label)
                data.setdefault("__range", {})[gb["groupby"]] = {
                    "from": range_start,
                    "to": range_end,
                }
                d = [
                    "&",
                    (gb["field"], ">=", range_start),
                    (gb["field"], "<", range_end),
                ]
        elif ftype in ("date", "datetime"):
            # Set the __range of the group containing records with an unset
            # date/datetime field value to False.
            data.setdefault("__range", {})[gb["groupby"]] = False

        if d is None:
            d = [(gb["field"], "=", value)]
        sections.append(d)
    sections.append(domain)

    data["__domain"] = expression.AND(sections)
    if len(groupby) - len(annotated_groupbys) >= 1:
        data["__context"] = {"group_by": groupby[len(annotated_groupbys) :]}
    del data["id"]
    return data


BaseModel._read_group_format_result = _read_group_format_result
