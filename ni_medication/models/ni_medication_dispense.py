#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models


class MedicationDispense(models.Model):
    _name = "ni.medication.dispense"
    _description = "Medication Dispense"
    _inherit = [
        "ni.medication.abstract",
        "ni.workflow.event.mixin",
        "ni.identifier.mixin",
        "mail.thread",
    ]

    medication_request_id = fields.Many2one(
        "ni.medication.request", "Rx", required=False, help="Authorized Prescription"
    )

    reason_ids = fields.Many2many(related="encounter_id.reason_ids")
    reason_id = fields.Many2one(
        "ni.encounter.reason", "Indication", domain="[('id', 'in', reason_ids)]"
    )
    quantity = fields.Float(required=True)
    quantity_display = fields.Char(compute="_compute_quantity_display")
    days_supply = fields.Integer()
    occurrence = fields.Datetime("Handed Over")

    note = fields.Text(help="Further information")
    active = fields.Boolean(default=True)

    @property
    def _workflow_request_id(self):
        return self.medication_request_id.request_id

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

    @api.model_create_multi
    def create(self, vals):
        if (
            "state" in vals
            and vals["state"] == "completed"
            and "occurrence" not in vals
        ):
            vals["occurrence"] = fields.Datetime.now()
        return super(MedicationDispense, self).create(vals)

    def write(self, vals):
        if (
            "state" in vals
            and vals["state"] == "completed"
            and "occurrence" not in vals
        ):
            vals["occurrence"] = fields.Datetime.now()
        return super(MedicationDispense, self).write(vals)

    def action_print_label(self):
        return self.env.ref(
            "ni_medication.action_report_medication_dispense_label"
        ).report_action(self)

    @api.constrains("medication_request_id")
    def _check_rx(self):
        for rec in self.filtered_domain([("medication_request_id", "!=", False)]):
            rx = rec.medication_request_id
            if rx.state in ["draft", "active"]:
                rx.state = "completed"
