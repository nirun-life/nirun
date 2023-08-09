#  Copyright (c) 2021-2023. NSTDA

from odoo import _, api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    disability_card = fields.Boolean(
        help="Indicate patient have disability card or not",
        tracking=True,
    )
    disability_card_reason = fields.Text(
        help="Reason why patient not have disability card",
        tracking=True,
    )
    disability_ids = fields.Many2many(
        "ni.disability",
        "ni_patient_disability_rel",
        "patient_id",
        "disability_id",
        ondelete="restrict",
    )
    disability_count = fields.Integer(
        compute="_compute_disability_count", sudo_compute=True, store=True
    )
    disability_display = fields.Char(
        compute="_compute_disability_display",
        sudo_compute=True,
        string="With Disability",
    )

    @api.model
    def create(self, vals):
        self._prepare_disability_value(vals)
        return super(Patient, self).create(vals)

    def write(self, vals):
        self._prepare_disability_value(vals)
        return super(Patient, self).write(vals)

    def _prepare_disability_value(self, vals):
        if "disability_ids" in vals and vals["disability_ids"] == [(6, 0, [])]:
            vals["disability_card"] = False
            vals["disability_card_reason"] = False
        elif "disability_card" in vals and vals["disability_card"] is True:
            vals["disability_card_reason"] = False

    @api.depends("disability_ids")
    def _compute_disability_count(self):
        for rec in self:
            rec.disability_count = len(rec.disability_ids)

    @api.depends("disability_ids")
    def _compute_disability_display(self):
        for rec in self:
            if len(rec.disability_ids) > 1:
                rec.disability_display = _("Multiple Disabilities")
            elif len(rec.disability_ids) == 1:
                rec.disability_display = rec.disability_ids[0].name
            else:
                rec.disability_display = None
