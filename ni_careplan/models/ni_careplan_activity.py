#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class CareplanActivity(models.Model):
    _name = "ni.careplan.activity"
    _description = "Careplan Activity"
    _inherits = ["ni.timing.mixin"]
    _order = "sequence"

    sequence = fields.Integer()
    careplan_id = fields.Many2one("ni.careplan", required=True, index=True)

    res_model = fields.Selection(
        [
            ("ni.service.request", "Service"),
            ("ni.medication.request", "Medication"),
        ]
    )
    res_id = fields.Many2oneReference(model_field="res_model")

    service_id = fields.Many2one("ni.service")
    medication_id = fields.Many2one("ni.medication")
