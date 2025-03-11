#  Copyright (c) 2023 NSTDA
import pprint

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MedicationAbstract(models.AbstractModel):
    _name = "ni.medication.abstract"
    _description = "Medication Abstract Resource"
    _inherits = {"ni.medication.dosage": "dosage_id"}
    _rec_name = "name"

    name = fields.Char("Medication Name", required=True)
    category_id = fields.Many2one("ni.medication.admin.location")
    medication_id = fields.Many2one("ni.medication", required=False)
    medication_dosage_ids = fields.Many2many(related="medication_id.dosage_ids")
    medication_dosage_count = fields.Integer(related="medication_id.dosage_count")
    medication_dose_unit_id = fields.Many2one(related="medication_id.dose_unit_id")
    medication_image_1920 = fields.Image(related="medication_id.image_1920")
    medication_image_1024 = fields.Image(related="medication_id.image_1024")
    medication_image_512 = fields.Image(related="medication_id.image_512")
    medication_image_256 = fields.Image(related="medication_id.image_256")
    medication_image_128 = fields.Image(related="medication_id.image_128", store=True)

    custom_checkbox_medication = fields.Boolean(
        string="Custom Medication", default=False
    )
    # custom_checkbox_dosage = fields.Boolean(string="Custom Dosage", default=False)

    dosage_id = fields.Many2one(
        "ni.medication.dosage", required=True, ondelete="cascade"
    )
    dosage_name = fields.Char(related="dosage_id.name")
    dosage_display = fields.Char(
        string="Dosage Summary", related="dosage_id.display_name"
    )

    dosage_tmpl_id = fields.Many2one(
        "ni.medication.dosage",
        "Dosage Template",
        store=False,
        help="Internal: only use to choose from medication's dosage choices",
        domain="[('id','in', medication_dosage_ids)]",
    )
    dosage_when = fields.Many2many(
        related="dosage_id.timing_when", help="Use for search filter with `When`"
    )

    @api.onchange("medication_id")
    def _onchange_medication_id(self):
        for rec in self:
            if rec.medication_id:
                rec.name = rec.medication_id.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("dosage_tmpl_id") and not vals.get("dosage_id"):
                vals["dosage_id"] = vals.get("dosage_tmpl_id")
        return super(MedicationAbstract, self).create(vals_list)

    def write(self, vals):
        if vals.get("dosage_tmpl_id") and not vals.get("dosage_id"):
            vals["dosage_id"] = vals.get("dosage_tmpl_id")
        return super().write(vals)

    @api.onchange("medication_id")
    def _onchange_medication(self):
        if self.dosage_tmpl_id:
            self.dosage_tmpl_id = False
        if self.medication_dose_unit_id:
            self.dose_unit_id = self.medication_dose_unit_id

    @api.onchange("dosage_tmpl_id")
    def _onchange_dosage_tmpl_id(self):
        for rec in self:
            if rec.dosage_tmpl_id:
                dosage = rec.dosage_tmpl_id.copy_data()[0]
                dosage = {k: v for k, v in dosage.items() if k in self._fields}
                dosage["dosage_name"] = dosage.pop("name")
                rec.update(dosage)

    @api.onchange("route_id")
    def _onchange_route_id(self):
        for rec in self:
            if rec.route_id and rec.route_id.method_id:
                rec.method_id = rec.route_id.method_id

    def save_dosage_as_template(self):
        if not self.medication_id:
            raise UserError(_("Must save medication link"))
        dosage = self.env["ni.medication.dosage"]
        def_val = {"name": self.dosage_name}
        dosage_val = {
            k: v for k, v in self.copy_data(def_val)[0].items() if k in dosage._fields
        }
        pprint.pprint(dosage_val)
        self.medication_id.write({"dosage_ids": [fields.Command.create(dosage_val)]})

    def reset_dosage_template(self):
        for rec in self:
            if rec.dosage_id:
                rec.timing_type = ""
                rec.dosage_id.timing_type = ""
                rec.dosage_id.dose = 0
                rec.dosage_id.additional_ids = False
                rec.dosage_id.as_need = False
                rec.dosage_id._update_timing_type()

    @api.onchange("timing_bound_start", "timing_bound_end")
    def _onchange_timing_bounds(self):
        for rec in self:
            if rec.dosage_id and rec.dosage_id.timing_id:
                rec.dosage_id.timing_id.bound_start = self.timing_bound_start
                rec.dosage_id.timing_id.bound_end = self.timing_bound_end
                rec.dosage_id.timing_id._compute_bound_duration()
                rec.timing_bound_duration_days = (
                    rec.dosage_id.timing_id.bound_duration_days
                )

    @api.onchange("timing_bound_duration_days")
    def _onchange_timing_bound_duration(self):
        for rec in self:
            if rec.dosage_id and rec.dosage_id.timing_id:
                rec.dosage_id.timing_id.bound_duration_days = (
                    self.timing_bound_duration_days
                )
                rec.dosage_id.timing_id._inverse_bound_duration()
                rec.timing_bound_start = self.dosage_id.timing_id.bound_start
                rec.timing_bound_end = self.dosage_id.timing_id.bound_end

    @api.onchange("dose")
    def _onchange_dose(self):
        for rec in self:
            if rec.dosage_id and rec.dosage_id.timing_id:
                rec.dosage_id._compute_display_name()

    @api.onchange("meal_timing", "meal_period_ids", "period_ids", "meal_offset")
    def _onchange_timing_when(self):
        for rec in self:
            if rec.dosage_id and rec.dosage_id.timing_id:
                rec.dosage_id._update_timing_when()

    @api.onchange("timing_type")
    def _onchange_timing_type(self):
        for rec in self:
            if rec.dosage_id and rec.dosage_id.timing_id:
                rec.dosage_id._update_timing_type()

    @api.onchange(
        "timing_frequency",
        "timing_frequency_max",
    )
    def _onchange_timing_frequency(self):
        for rec in self:
            if rec.dosage_id and rec.dosage_id.timing_id:
                rec.dosage_id.timing_id.frequency = self.timing_frequency
                rec.dosage_id.timing_id.frequency_max = self.timing_frequency_max
                rec.dosage_id._compute_display_name()

    @api.onchange(
        "timing_duration",
        "timing_duration_max",
        "timing_duration_unit",
    )
    def _onchange_timing_duration(self):
        for rec in self:
            if rec.dosage_id and rec.dosage_id.timing_id:
                # ตรวจสอบว่ามีการเปลี่ยนแปลง timing_duration_max
                if (
                    self._origin
                    and self.timing_duration_max != self._origin.timing_duration_max
                ):
                    rec.dosage_id.timing_id.duration_max = self.timing_duration_max

                # ตรวจสอบและอัปเดต timing_duration
                if rec.timing_duration != self._origin.timing_duration:
                    rec.dosage_id.timing_id.duration = self.timing_duration

                # ตรวจสอบและอัปเดต timing_duration_unit
                if rec.timing_duration_unit != self._origin.timing_duration_unit:
                    rec.dosage_id.timing_id.duration_unit = self.timing_duration_unit

                rec.dosage_id._compute_display_name()

    @api.onchange(
        "timing_period",
        "timing_period_max",
        "timing_period_unit",
    )
    def _onchange_timing_period(self):
        for rec in self:
            if rec.dosage_id and rec.dosage_id.timing_id:
                rec.dosage_id.timing_id.period_unit = self.timing_period_unit
                rec.dosage_id.timing_id.period = self.timing_period
                rec.dosage_id.timing_id.period_max = self.timing_period_max
                rec.dosage_id._compute_display_name()
