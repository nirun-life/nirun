#  Copyright (c) 2026 NSTDA
from odoo import api, fields, models


class Flag(models.Model):
    _name = "ni.flag"
    _description = "Flag"
    _inherit = ["ni.period.mixin", "ni.patient.res", "ni.identifier.mixin"]
    _order = "period_start DESC, id DESC"
    _check_period_start = False
    _identifier_ts_field = "period_start"

    status = fields.Selection(
        [
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("entered-in-error", "Entered in Error"),
        ],
        required=True,
        default="active",
        index=True,
        copy=False,
    )
    category_ids = fields.Many2many(
        "ni.flag.category",
        "ni_flag_category_rel",
        "flag_id",
        "category_id",
    )
    code_id = fields.Many2one(
        "ni.flag.code",
        "Flag",
        required=True,
        ondelete="restrict",
        index=True,
    )
    code = fields.Char(related="code_id.code", store=True)
    color = fields.Integer(related="code_id.color", store=True)
    author_id = fields.Many2one(
        "res.users",
        "Author",
        default=lambda self: self.env.user,
    )
    note = fields.Text()

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        return self.code_id.name if self.code_id else self.identifier

    def action_active(self):
        self.write({"status": "active", "period_end": False})

    def action_inactive(self):
        self.write({"status": "inactive", "period_end": fields.Datetime.now()})

    def action_entered_in_error(self):
        self.write({"status": "entered-in-error", "period_end": fields.Datetime.now()})

    @api.model
    def garbage_collect(self, max_age_seconds=60):
        """Remove accidental flags: inactive with duration under max_age_seconds."""
        candidates = self.search(
            [("status", "=", "inactive"), ("period_end", "!=", False)]
        )
        to_unlink = candidates.filtered(
            lambda r: r.period_start
            and (r.period_end - r.period_start).total_seconds() < max_age_seconds
        )
        to_unlink.unlink()
