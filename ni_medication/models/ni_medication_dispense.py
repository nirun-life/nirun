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
    quantity = fields.Float()
    quantity_display = fields.Char(compute="_compute_quantity_display")
    days_supply = fields.Integer()
    occurrence = fields.Datetime("Handed Over")

    note = fields.Text(help="Further information")
    active = fields.Boolean(default=True)

    @api.depends("quantity", "dose_unit_id")
    def _compute_quantity_display(self):
        for rec in self:
            quantity = (
                int(rec.quantity)
                if rec.quantity.is_integer()
                else round(self.quantity, 2)
            )
            rec.quantity_display = "{} {}".format(quantity, rec.dose_unit_id)

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
        return self.env.ref("ni_medication.action_report_op_label").report_action(self)
