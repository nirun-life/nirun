#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    group_ids = fields.Many2many(
        "ni.patient.group",
        "ni_patient_group_rel",
        "patient_id",
        "group_id",
        string="Groups",
        check_company=True,
    )
