#  Copyright (c) 2025 NSTDA
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DeviceDefinition(models.Model):
    _name = "ni.device.definition"
    _description = "Device Definition"
    _inherit = ["image.mixin", "mail.thread"]
    _rec_name = "name"
    _order = "name"

    name = fields.Char(
        string="Definition Name",
        required=True,
        tracking=True,
        help="The name/model of the device, e.g., portable blood pressure monitor, arm-type blood pressure monitor",
    )

    type_ids = fields.Many2many(
        "ni.device.type",
        string="Device Types",
        required=False,
        help="The type of device, e.g., blood pressure monitor, weighing scale",
    )

    manufacturer_id = fields.Many2one(
        "res.partner",
        string="Manufacturer",
        domain="[('is_company', '=', True)]",
        tracking=True,
    )

    model_number = fields.Char("Model Number", tracking=True)

    observation_type_ids = fields.Many2many(
        "ni.observation.type",
        string="Supported Observation Types",
        help="Types of measurements supported by this device model",
    )

    notes = fields.Html("Notes")

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )

    device_ids = fields.One2many(
        "ni.device",
        "definition_id",
        string="Devices",
    )

    device_count = fields.Integer(compute="_compute_device_count", store=True)

    usage_count = fields.Integer(compute="_compute_usage_count")

    @api.depends("device_ids")
    def _compute_device_count(self):
        for rec in self:
            rec.device_count = len(rec.device_ids)

    def _compute_usage_count(self):
        for rec in self:
            rec.usage_count = self.env["ni.device.usage"].search_count(
                [("device_id", "in", rec.device_ids.ids)]
            )

    def action_view_devices(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Devices",
            "res_model": "ni.device",
            "view_mode": "kanban,tree,form",
            "domain": [("definition_id", "=", self.id)],
            "context": {"default_definition_id": self.id},
        }

    def action_view_usage(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Device Usage Logs",
            "res_model": "ni.device.usage",
            "view_mode": "kanban,tree,form",
            "domain": [("device_id", "in", self.device_ids.ids)],
            "context": {"search_default_group_device": 1},
        }
