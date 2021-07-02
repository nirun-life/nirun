#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class MedicationStatement(models.Model):
    _name = "ni.medication.statement"
    _description = "Medication Statement"
    _inherit = [
        "ni.patient.res",
        "period.mixin",
        "mail.thread",
        "mail.activity.mixin",
        "image.mixin",
    ]

    name = fields.Char(related="medication_id.name", store=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    location_id = fields.Many2one(
        related="encounter_id.location_id", store=True, index=True, tracking=True
    )
    category_id = fields.Many2one(
        "ni.medication.statement.category",
        "Category",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    medication_id = fields.Many2one(
        "ni.medication", required=True, ondelete="restrict", tracking=True
    )
    image_1920 = fields.Image(related="medication_id.image_1920")
    image_1024 = fields.Image(related="medication_id.image_1024")
    image_512 = fields.Image(related="medication_id.image_512")
    image_256 = fields.Image(related="medication_id.image_256")
    image_128 = fields.Image(related="medication_id.image_128")
    state = fields.Selection(
        [("active", "Currently"), ("completed", "Completed"), ("stopped", "Stopped")],
        default="active",
        required=True,
        tracking=True,
    )
    state_reason = fields.Char(required=False, tracking=True)
    period_start = fields.Date(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    dosage = fields.Text(
        help="How the medication is/was taken or should be taken", tracking=True
    )
    dosage_timing = fields.Many2one(
        "ni.timing",
        "Timing",
        help="When medication should be administered",
        auto_join=True,
        tracking=True,
    )
    dosage_when = fields.Many2many(
        string="Dosage (when)", related="dosage_timing.when", tracking=True
    )
    dosage_as_need = fields.Boolean("As need?", default=False, tracking=True)

    @api.depends("medication_id.name", "patient_id.name")
    def _compute_display_name(self):
        diff = dict(show_patient=True, show_period=None, show_state=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        rec = self
        name = rec.name or rec.medication_id.name
        if self._context.get("show_patient"):
            name = "{}, {}".format(rec.patient_id._name_get(), name)
        if self._context.get("show_period"):
            if rec.period_start and rec.period_end:
                name = "{}[{}-{}]".format(name, rec.period_start, rec.period_end)
            elif rec.period_start:
                name = "{}[{}]".format(name, rec.period_start)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, rec.get_state_label())
        return name

    def get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)
