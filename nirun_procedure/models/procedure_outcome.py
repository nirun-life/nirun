#  Copyright (c) 2022. NSTDA
from odoo import models


class ProcedureOutcome(models.Model):
    _name = "ni.procedure.outcome"
    _description = "Procedure Outcome"
    _inherit = ["coding.base"]
