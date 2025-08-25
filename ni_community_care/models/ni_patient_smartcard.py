#  Copyright (c) 2025 NSTDA
from odoo import api, fields, models


class PatientSmartcardActivity(models.Model):
    _name = "ni.patient.smartcard.service"

    smartcard_id = fields.Many2one(
        "ni.patient.smartcard", required=True, ondelete="cascade"
    )
    service_id = fields.Many2one("ni.service", required=True, ondelete="restrict")
    service_category_id = fields.Many2one(related="service_id.category_id")
    color = fields.Integer(related="service_id.category_id.color")


class PatientSmartcard(models.Model):
    _inherit = "ni.patient.smartcard"

    service_ids = fields.One2many("ni.patient.smartcard.service", "smartcard_id")

    service_count = fields.Integer(compute="_compute_service_count")

    @api.depends("service_ids")
    def _compute_service_count(self):
        for rec in self:
            rec.service_count = len(rec.service_ids)
            fields.Command.create({})
