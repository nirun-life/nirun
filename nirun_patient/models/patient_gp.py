#  Copyright (c) 2021 Piruin P.

from odoo import _, fields, models


class GeneralPractitioner(models.Model):
    _name = "ni.patient.gp"
    _description = "General Practitioner"
    _order = "sequence"

    sequence = fields.Integer()
    patient_id = fields.Many2one("ni.patient", ondelete="cascade")
    practitioner_id = fields.Many2one("res.partner", ondelete="cascade")
    practitioner_company_id = fields.Many2one(
        related="practitioner_id.commercial_partner_id"
    )
    note = fields.Text()

    _sql_constraints = [
        (
            "patient_practitioner_uniq",
            "unique (patient_id, practitioner_id)",
            _("Duplicate practitioner!"),
        ),
    ]
