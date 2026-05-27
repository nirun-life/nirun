#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    disability_encounter_priority = fields.Selection(
        [
            ("routine", "Routine"),
            ("urgent", "Urgent"),
            ("asap", "ASAP"),
            ("stat", "STAT"),
        ],
        string="Disability Encounter Priority",
        help="Default triage priority for new encounters when the patient has a disability. Leave blank to disable.",
    )
