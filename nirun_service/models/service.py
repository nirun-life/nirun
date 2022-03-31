#  Copyright (c) 2021 Piruin P.

import math

from odoo import api, fields, models


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
    request_count = fields.Integer("Participant", compute="_compute_request_count")

    @api.depends("request_ids")
    def _compute_request_count(self):
        res = self._count_active_request()
        for rec in self:
            rec.request_count = res.get(rec.id, 0)

    def _count_active_request(self):
        _domain = [("service_id", "in", self.ids), ("state", "=", "active")]
        req = self.env["ni.service.request"].read_group(
            _domain,
            ["service_id"],
            ["service_id"],
        )
        return {data["service_id"][0]: data["service_id_count"] for data in req}

    def open_request(self, state="active"):
        self.ensure_one()
        ctx = dict(self._context)
        ctx.update(
            {
                "search_default_service_id": self.id,
                "search_default_%s" % state: True,
                "default_service_id": self.id,
            }
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_service", "service_request_action"
        )
        return dict(action, context=ctx)
