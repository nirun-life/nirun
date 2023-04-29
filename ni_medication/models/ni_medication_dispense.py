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
    days_supply = fields.Integer()
    occurrence = fields.Datetime("Handed Over")

    note = fields.Text(help="Further information")
    active = fields.Boolean(default=True)

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
