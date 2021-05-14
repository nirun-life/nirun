#  Copyright (c) 2021 Piruin P.

import math

from odoo import fields, models


def float_time_convert(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    return factor * int(math.floor(val)), int(round((val % 1) * 60))


def float_time_format(float_val):
    h, m = float_time_convert(float_val)
    return "%0d:%02d" % (h, m)


class HealthcareService(models.Model):
    _name = "ni.service"
    _description = "Healthcare Service"
    _inherit = ["mail.thread", "image.mixin", "coding.base"]

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    name = fields.Char(index=True)
    active = fields.Boolean(default=True)
    code = fields.Char("Internal Reference", index=True)
    category_ids = fields.Many2many(
        "ni.service.category",
        "ni_service_category_rel",
        "service_id",
        "category_id",
        help="Broad category of service being performed or delivered",
    )
    location_ids = fields.Many2many(
        "ni.location",
        "ni_service_location",
        "service_id",
        "location_id",
        help="Location(s) where service may be provided",
        ondelete="cascade",
    )
    comment = fields.Text(
        "Internal Notes",
        help="Additional description and/or any specific issues not covered elsewhere",
    )

    available_type = fields.Selection(
        [("routine", "Routine "), ("event", "Event")],
        default="routine",
        required=True,
        help="""Whether service is routine or base on event.
         Technical: time_ids for routine, timing_ids for event""",
    )
    available_time_ids = fields.One2many(
        "ni.service.time",
        "service_id",
        "Available Times",
        help="Times the Service is available",
    )
    available_timing_ids = fields.One2many(
        "ni.service.timing",
        "service_id",
        "Recurrent",
        help="When the Service is to occur",
    )

    request_ids = fields.One2many("ni.service.request", "service_id")
