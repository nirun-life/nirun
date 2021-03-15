#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    talent = fields.Text()
    face = fields.Text()
    skin = fields.Text()
    flaw = fields.Text()
    conversation = fields.Text()
    demeanor = fields.Text()
