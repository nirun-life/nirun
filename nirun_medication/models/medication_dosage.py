#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


class Dosage(models.Model):
    _name = "ni.medication.dosage"
    _description = "Dosage"
    _order = "sequence"

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
    timing_id = fields.Many2one(
        "ni.timing",
        "Timing",
        auto_join=True,
        index=True,
        ondelete="cascade",
        required=True,
        tracking=True,
    )
    timing_tmpl_id = fields.Many2one("ni.timing.template", store=False)
    timing_when = fields.Many2many(related="timing_id.when")

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

    @api.model
    def create(self, vals):
        if vals.get("timing_tmpl_id") and not vals.get("timing_id"):
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            vals["timing_id"] = tmpl.to_timing().ids[0]
        return super(Dosage, self).create(vals)

    def update(self, vals):
        if vals.get("timing_tmpl_id") and not vals.get("timing_id"):
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            vals["timing_id"] = tmpl.to_timing().ids[0]
        return super(Dosage, self).update(vals)

    def _get_timing_tmpl(self, ids):
        return self.env["ni.timing.template"].browse(ids)
