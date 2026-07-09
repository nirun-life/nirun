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

    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    price = fields.Monetary(
        "Default Price",
        currency_field="currency_id",
        tracking=True,
        help="Applied to a new device only when the device's own price is not yet set.",
    )

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

    @api.depends("device_ids.usage_ids")
    def _compute_usage_count(self):
        data = self.env["ni.device.usage"].read_group(
            [("definition_id", "in", self.ids)], ["definition_id"], ["definition_id"]
        )
        counts = {d["definition_id"][0]: d["definition_id_count"] for d in data}
        for rec in self:
            rec.usage_count = counts.get(rec.id, 0)

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
