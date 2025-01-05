#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class Dosage(models.Model):
    _name = "ni.medication.dosage"
    _description = "Dosage"
    _order = "sequence"
    _inherit = ["ni.timing.mixin"]

    sequence = fields.Integer(default=16)
    name = fields.Char()
    display_name = fields.Char(compute="_compute_display_name")
    color = fields.Integer(related="route_id.color")
    text = fields.Text(
        help="How the medication is/was taken or should be taken",
    )
    additional_ids = fields.Many2many(
        "ni.medication.dosage.additional",
        "ni_medication_dosage_additional_rel",
        "dosage_id",
        "additional_id",
        string="Additional Instruction",
        help="Supplemental instruction or warnings to the patient - "
        'e.g. "with meals", "may cause drowsiness"',
    )
    timing_type = fields.Selection(
        [
            ("meal", "Meal"),
            ("period", "Period"),
            ("custom", "Other"),
        ],
        string="Timing Type",
        default="meal",
    )

    period_ids = fields.Many2many(
        "ni.medication.dosage.period",
        string="Dosage Periods",
        help="Select the periods for medication intake (e.g., Morning, Afternoon, etc.).",
    )

    meal_timing = fields.Selection(
        [
            ("C", "With meal"),
            ("AC", "Before a meal"),
            ("PC", "After a meal"),
        ],
        string="Meal Timing",
        default="C",
    )

    meal_offset = fields.Integer()

    site_id = fields.Many2one(
        "ni.body.site", "Body Site", help="Body site to administer to"
    )
    route_id = fields.Many2one(
        "ni.medication.dosage.route", "Route", help="How drug should enter body"
    )
    method_id = fields.Many2one(
        "ni.medication.dosage.method",
        "Method",
        help="Technique for administering medication",
    )
    as_need = fields.Boolean("As need?", default=False, help='Take "as needed"')
    dose = fields.Float(help="Amount of medication per dose")
    dose_unit_id = fields.Many2one("uom.uom", help="Unit of medication per dose")
    display_dose = fields.Char(
        compute="_compute_display_dose", help="Amount of medication per dose"
    )

    @api.depends("dose", "dose_unit_id")
    def _compute_display_dose(self):
        for rec in self:
            if rec.dose and rec.dose_unit_id:
                unit = rec.dose_unit_id.alias or rec.dose_unit_id.name
                if rec.dose.is_integer():
                    rec.display_dose = "{:d} {}".format(int(rec.dose), unit)
                else:
                    rec.display_dose = "{} {}".format(rec.dose, unit)
            else:
                rec.display_dose = None

    @api.depends("timing_id", "text", "additional_ids")
    def _compute_display_name(self):
        diff = dict(show_text=None, show_additional=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        rec = self
        name = rec.timing_id.name
        if self.route_id:
            name = "{} {}".format(self.route_id.abbr or self.route_id.name, name)
        if self.display_dose:
            name = "{} {}".format(self.display_dose, name)
        if self._context.get("show_text") and self.text:
            name = "{}\n{}".format(name, rec.text)
        if self._context.get("show_additional") and self.additional_ids:
            additional = ", ".join(rec.additional_ids.mapped("name"))
            name = "{}\n{}".format(name, additional)
        return name

    @api.onchange("timing_type")
    def _update_timing_type(self):
        for record in self:
            record.meal_timing = "C"
            record.period_ids = [(5, 0, 0)]
            record.timing_id.time_of_day = [(5, 0, 0)]
            record.timing_frequency_max = 0
            record.timing_frequency = 1
            record.timing_duration_max = 0
            record.timing_duration = 0
            record.timing_duration_unit = False
            record.timing_period_max = 0
            record.timing_period = 1
            record.timing_period_unit = "day"
            record.timing_id.when = [(5, 0, 0)]
            record._update_timing_when()

    @api.onchange("meal_timing", "period_ids", "meal_offset")
    def _update_timing_when(self):
        for record in self:
            record.timing_id.offset = 0
            if record.timing_id:
                record.timing_id.when = [(5, 0, 0)]

            # เช็ค timing_type เป็น meal หรือ period
            if record.timing_type == "meal" and record.meal_timing:
                record._update_timing_when_meal()
            elif record.timing_type == "period" and record.period_ids:
                record._update_timing_when_period()

            # อัปเดต offset หลังสุด
            record._update_timing_offset()

            # อัปเดต display_name หลังสุด
            record._compute_display_name()

    # Method สำหรับ timing_type == "meal"
    def _update_timing_when_meal(self):
        for record in self:
            # เช็คว่า period_ids มีค่าหนึ่งใน ['M', 'D', 'V']
            if any(period.code in ["M", "D", "V"] for period in record.period_ids):
                # ถ้ามี period_ids ที่ตรงกับ 'M', 'D', 'V', เอา meal_timing มาต่อกับ period.code
                codes_to_match = [
                    f"{record.meal_timing}{period.code}" for period in record.period_ids
                ]
            else:
                # ถ้าไม่มี period_ids ที่ตรงกับ 'M', 'D', 'V', ใช้ meal_timing อย่างเดียว
                codes_to_match = [record.meal_timing]

            # ค้นหาจาก code ที่ได้จาก codes_to_match
            matching_when_ids = self.env["ni.timing.event"].search(
                [("code", "in", codes_to_match)]
            )

            # อัปเดต timing_id.when ด้วยผลลัพธ์จากการค้นหา
            if matching_when_ids:
                record.timing_id.when = [(6, 0, matching_when_ids.ids)]
            else:
                # ถ้าไม่พบการจับคู่ใดๆ ให้รีเซ็ต timing_id.when
                record.timing_id.when = [(5, 0, 0)]  # หรือค่า default อื่นๆ

    # Method สำหรับ timing_type == "period"
    def _update_timing_when_period(self):
        for record in self:
            if record.period_ids:
                codes_to_match = [period.code for period in record.period_ids]
                matching_when_ids = self.env["ni.timing.event"].search(
                    [("code", "in", codes_to_match)]
                )
                record.timing_id.when = [(6, 0, matching_when_ids.ids)]

    # Method สำหรับการตั้งค่า offset
    def _update_timing_offset(self):
        for record in self:
            if record.timing_type != "meal" or record.meal_timing == "C":
                record.timing_id.offset = 0
            else:
                record.timing_id.offset = record.meal_offset
