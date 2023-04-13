#  Copyright (c) 2022-2023 NSTDA

from odoo import api, fields, models


class TimingMixin(models.AbstractModel):
    _name = "ni.timing.mixin"
    _description = "Timing"

    timing_id = fields.Many2one(
        "ni.timing.timing",
        auto_join=True,
        ondelete="set null",
        tracking=True,
        domain=[
            ("res_model", "=", lambda self: self._name),
            ("res_id", "=", lambda self: self.id),
        ],
    )
    timing_tmpl_id = fields.Many2one("ni.timing.template", store=False)
    timing_when = fields.Many2many(related="timing_id.when")
    timing_dow = fields.Many2many(related="timing_id.day_of_week")
    timing_tod = fields.One2many(related="timing_id.time_of_day")

    @api.model
    def create(self, vals):
        if vals.get("timing_tmpl_id") and not vals.get("timing_id"):
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            vals["timing_id"] = tmpl.to_timing().ids[0]

        record = super(TimingMixin, self).create(vals)

        if record.timing_id:
            record.timing_id.write({"res_model": record._name, "res_id": record.id})
        return record

    def write(self, vals):
        timing_tmpl = vals.get("timing_tmpl_id") and not vals.get("timing_id")
        if len(self) == 1 and timing_tmpl:
            # if update only one record it easily done
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            vals["timing_id"] = tmpl.to_timing(
                {"res_model": self._name, "res_id": self.id}
            ).ids[0]
            return super(TimingMixin, self).write(vals)

        success = super(TimingMixin, self).write(vals)
        if timing_tmpl:
            # create timing record for each record that were write
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            for rec in self:
                rec.timing_id = tmpl.to_timing(
                    {"res_model": rec._name, "res_id": rec.id}
                ).ids[0]
        return success

    def _get_timing_tmpl(self, ids):
        return self.env["ni.timing.template"].browse(ids)

    def unlink(self):
        """Override unlink to delete timing. This cannot be
        cascaded, because link is done through (res_model, res_id)."""
        if not self:
            return True
        self.env["ni.timing.timing"].search(
            [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        ).sudo().unlink()
        return super(TimingMixin, self).unlink()
