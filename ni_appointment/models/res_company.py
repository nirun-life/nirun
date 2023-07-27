#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    _description = "Company"

    appointment_instruction_ids = fields.Many2many(
        "ni.appointment.instruction", string="Patient Instruction"
    )
    appointment_duration = fields.Float(default=0.50)
