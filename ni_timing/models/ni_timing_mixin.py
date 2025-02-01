#  Copyright (c) 2022-2023 NSTDA

from odoo import api, fields, models


class TimingMixin(models.AbstractModel):
    _name = "ni.timing.mixin"
    _description = "Timing"

    timing_id = fields.Many2one(
        "ni.timing.timing",
        auto_join=True,
        ondelete="set null",
        domain=[
            ("res_model", "=", lambda self: self._name),
            ("res_id", "=", lambda self: self.id),
        ],
        default=lambda self: self._create_default_timing(),
    )

    @api.model
    def _create_default_timing(self):
        """
        Create a new ni.timing.timing record and return its ID as the default.
        """
        return (
            self.env["ni.timing.timing"]
            .create(
                {
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )
            .id
        )

    timing_tmpl_id = fields.Many2one("ni.timing.template", store=False)
    timing_when = fields.Many2many(related="timing_id.when")
    timing_dow = fields.Many2many(related="timing_id.day_of_week")
    timing_tod = fields.One2many(related="timing_id.time_of_day", readonly=False)

    # Fields for frequency
    timing_frequency = fields.Integer(related="timing_id.frequency", readonly=False)
    timing_frequency_max = fields.Integer(
        related="timing_id.frequency_max", readonly=False
    )

    # Fields for duration
    timing_duration = fields.Integer(related="timing_id.duration", readonly=False)
    timing_duration_max = fields.Integer(
        related="timing_id.duration_max", readonly=False
    )
    timing_duration_unit = fields.Selection(
        related="timing_id.duration_unit", readonly=False
    )

    # Fields for period
    timing_period = fields.Integer(related="timing_id.period", readonly=False)
    timing_period_max = fields.Integer(related="timing_id.period_max", readonly=False)
    timing_period_unit = fields.Selection(
        related="timing_id.period_unit", readonly=False
    )

    timing_offset = fields.Integer(related="timing_id.offset", readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("timing_tmpl_id") and not vals.get("timing_id"):
                tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
                vals["timing_id"] = tmpl.to_timing().ids[0]

        records = super(TimingMixin, self).create(vals_list)
        for rec in records:
            if rec.timing_id:
                rec.timing_id.write({"res_model": rec._name, "res_id": rec.id})
        return records

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
