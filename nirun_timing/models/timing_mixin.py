#  Copyright (c) 2022 Piruin P.

from odoo import api, fields, models


class TimingMixin(models.AbstractModel):
    _name = "ni.timing.mixin"
    _description = "Timing"

    timing_id = fields.Many2one(
        "ni.timing", auto_join=True, ondelete="restrict", tracking=True
    )
    timing_tmpl_id = fields.Many2one("ni.timing.template", store=False)
    timing_when = fields.Many2many(related="timing_id.when")

    @api.model
    def create(self, vals):
        if vals.get("timing_tmpl_id") and not vals.get("timing_id"):
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            vals["timing_id"] = tmpl.to_timing().ids[0]
        return super(TimingMixin, self).create(vals)

    def write(self, vals):
        if vals.get("timing_tmpl_id") and not vals.get("timing_id"):
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            vals["timing_id"] = tmpl.to_timing().ids[0]
        return super(TimingMixin, self).write(vals)

    def _get_timing_tmpl(self, ids):
        return self.env["ni.timing.template"].browse(ids)
