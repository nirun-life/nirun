#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class MedicationAdministrationLocation(models.Model):
    _name = "ni.medication.admin.location"
    _description = "Medication Statement Category"
    _inherit = ["ni.coding"]

    request = fields.Boolean(default=True)
    statement = fields.Boolean(default=True)
