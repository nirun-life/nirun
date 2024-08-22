#  Copyright (c) 2023 NSTDA
from odoo import api, fields, models


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
    medication_image_128 = fields.Image(related="medication_id.image_128")
    dosage_id = fields.Many2one(
        "ni.medication.dosage", required=True, ondelete="cascade"
    )
    dosage_name = fields.Char(related="dosage_id.name")
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
