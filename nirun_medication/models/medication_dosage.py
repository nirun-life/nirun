#  Copyright (c) 2021 NSTDA
from odoo import api, fields, models


class Dosage(models.Model):
    _name = "ni.medication.dosage"
    _description = "Dosage"
    _order = "sequence"
    _inherit = ["ni.timing.mixin"]

    sequence = fields.Integer(default=16)
    name = fields.Char()
    display_name = fields.Char(compute="_compute_display_name")
    color = fields.Integer()
    text = fields.Text(
        help="How the medication is/was taken or should be taken", tracking=True
    )
    additional_ids = fields.Many2many(
        "ni.medication.dosage.additional",
        "ni_medication_dosage_additional_rel",
        "dosage_id",
        "additional_id",
        stirng="Additional Instruction",
        help="Supplemental instruction or warnings to the patient - "
        'e.g. "with meals", "may cause drowsiness"',
    )

    site_id = fields.Many2one(
        "ni.medication.dosage.site", "Body Site", help="Body site to administer to"
    )
    route_id = fields.Many2one(
        "ni.medication.dosage.route", "Route", help="How drug should enter body"
    )
    method_id = fields.Many2one(
        "ni.medication.dosage.method",
        "Method",
        help="Technique for administering medication",
    )
    as_need = fields.Boolean("As need?", default=False, tracking=True)

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
        if self._context.get("show_text") and self.text:
            name = "{}\n{}".format(name, rec.text)
        if self._context.get("show_additional") and self.additional_ids:
            additional = ", ".join(rec.additional_ids.mapped("name"))
            name = "{}\n{}".format(name, additional)
        return name
