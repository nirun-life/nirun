#  Copyright (c) 2021 NSTDA

from odoo import models


class DosageRoute(models.Model):
    _name = "ni.medication.dosage.route"
    _description = "Medication Route"
    _inherit = ["coding.base"]
    # Route may also be use at Allergy.reaction in future
