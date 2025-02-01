#  Copyright (c) 2024 NSTDA

import pprint

from odoo import api, fields, models


class MedicationRequest(models.Model):
    _name = "ni.medication.request"
    _description = "Medication Request"
    _inherit = [
        "ni.workflow.request.mixin",
        "ni.medication.abstract",
        "ni.identifier.mixin",
    ]

    reason_ids = fields.Many2many(related="encounter_id.reason_ids")
    reason_id = fields.Many2one(
        "ni.encounter.reason", "Indication", domain="[('id', 'in', reason_ids)]"
    )

    quantity = fields.Float(required=True)
    quantity_display = fields.Char(
        compute="_compute_quantity_display", store=True, readonly=False
    )
    days_supply = fields.Integer()
    note = fields.Text()
    color = fields.Integer(related="dosage_id.color")
    medication_dispense_ids = fields.One2many(
        "ni.medication.dispense", "medication_request_id"
    )
    medication_dispense_count = fields.Integer(
        compute="_compute_medication_dispense_count"
    )

    @api.depends("medication_dispense_ids")
    def _compute_medication_dispense_count(self):
        for rec in self:
            rec.medication_dispense_count = len(rec.medication_dispense_ids)

    @api.depends("quantity", "medication_dose_unit_id")
    def _compute_quantity_display(self):
        for rec in self:
            quantity = (
                int(rec.quantity)
                if rec.quantity.is_integer()
                else round(self.quantity, 2)
            )
            if rec.medication_dose_unit_id:
                rec.quantity_display = "{} {}".format(
                    quantity, rec.medication_dose_unit_id.name
                )
            else:
                rec.quantity_display = str(quantity)

    def action_dispense(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        request = self.copy_data()[0]

        ctx.update({"isCopy": True})

        ctx.update(
            {
                "default_{}".format(k): v
                for k, v in request.items()
                if k in self.env["ni.medication.dispense"]._fields
            }
        )
        ctx.update(
            {
                "default_medication_request_id": self.id,
                "default_request_id": self.request_id.id,
            }
        )
        pprint.pprint(ctx)
        view = {
            "name": "Dispense",
            "res_model": "ni.medication.dispense",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "new"),
            "view_type": "form",
            "views": [[False, "form"]],
            "context": ctx,
        }
        return view

    @api.onchange("quantity", "medication_dose_unit_id")
    def _onchange_quantity_display(self):
        for rec in self:
            rec._compute_quantity_display()

    def action_save_draft(self):
        for rec in self:
            rec.state = "draft"

    def copy_data(self, default=None):
        default = dict(default or {})

        # คัดลอกค่าจาก original record
        copied_vals = super().copy_data(default)[0]

        # คัดลอกค่าจาก timing_id
        if self.timing_id:
            copied_vals.update(
                {
                    "timing_frequency": self.timing_frequency,
                    "timing_frequency_max": self.timing_frequency_max,
                    "timing_duration": self.timing_duration,
                    "timing_duration_max": self.timing_duration_max,
                    "timing_duration_unit": self.timing_duration_unit,
                    "timing_period": self.timing_period,
                    "timing_period_max": self.timing_period_max,
                    "timing_period_unit": self.timing_period_unit,
                    "timing_offset": self.timing_offset,
                    "timing_tmpl_id": self.timing_tmpl_id.id
                    if self.timing_tmpl_id
                    else False,
                }
            )

            # คัดลอก Many2many และ One2many
            copied_vals["timing_when"] = (
                [(6, 0, self.timing_when.ids)] if self.timing_when else [(5, 0, 0)]
            )
            copied_vals["timing_dow"] = (
                [(6, 0, self.timing_dow.ids)] if self.timing_dow else [(5, 0, 0)]
            )
            copied_vals["timing_tod"] = (
                [(6, 0, self.timing_tod.ids)] if self.timing_tod else [(5, 0, 0)]
            )

        return [copied_vals]
