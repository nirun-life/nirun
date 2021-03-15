#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class PatientContact(models.Model):
    _name = "ni.patient.contact"
    _order = "patient_id, sequence, relationship"
    _description = "Contacts of Patent"

    sequence = fields.Integer(
        "Sequence", help="Determine the display order", index=True, default=10
    )
    patient_id = fields.Many2one(
        "ni.patient", string="Patient Reference", ondelete="cascade", require=True
    )
    contact_id = fields.Many2one("res.partner", ondelete="cascade", require=True)
    relationship = fields.Many2one(
        "ni.patient.relationship",
        help="How this contract relate to patient",
        ondelete="restrict",
        require=True,
    )
    is_contactable = fields.Boolean(
        "Contactable?", help="Whether can you contact with this one?", default=True
    )
    comment = fields.Text("Internal Note")

    _sql_constraints = [
        ("uniq", "unique (patient_id, contact_id)", "Contact already added!",),
    ]
