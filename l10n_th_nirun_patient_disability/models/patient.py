#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    disability_card = fields.Boolean(
        help="Indicate patient have disability card or not"
    )
    disability_card_reason = fields.Text(
        help="Reason why patient not have disability card"
    )
    disability_ids = fields.Many2many(
        "ni.disability",
        "ni_patient_disability_rel",
        "patient_id",
        "disability_id",
        ondelete="restrict",
    )
    disability_display = fields.Char(
        compute="_compute_disability_display",
        sudo_compute=True,
        string="With Disability",
    )

    @api.depends("disability_ids")
    def _compute_disability_display(self):
        for rec in self:
            if len(rec.disability_ids) > 1:
                rec.disability_display = _("Multiple Disabilities")
            elif len(rec.disability_ids) == 1:
                rec.disability_display = rec.disability_ids[0].name
            else:
                rec.disability_display = None
