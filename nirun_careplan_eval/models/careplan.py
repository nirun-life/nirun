#  Copyright (c) 2023. NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Careplan(models.Model):
    _inherit = "ni.careplan"

    achievement_date = fields.Datetime(store=True)
    pre_eval = fields.Text("Pre-Evaluation", tracking=True)
    pre_eval_date = fields.Datetime(
        readonly=True,
        tracking=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
    )
    post_eval = fields.Text("Post-Evaluation", tracking=True)
    post_eval_date = fields.Datetime(
        readonly=True,
        tracking=True,
        states={"completed": [("readonly", False)]},
    )

    @api.constrains("pre_eval_date", "period_start")
    def _check_pre_eval_date(self):
        for rec in self:
            if (
                rec.period_start
                and rec.pre_eval_date
                and not (rec.pre_eval_date.date() <= rec.period_start)
            ):
                raise ValidationError(
                    _("Pre-evaluation date must occurred before plan start date")
                )

    @api.constrains("post_eval_date", "period_start")
    def _check_post_eval_date(self):
        for rec in self:
            if (
                rec.period_end
                and rec.post_eval_date
                and not (rec.period_end <= rec.post_eval_date.date())
            ):
                raise ValidationError(
                    _("Post-evaluation date must occurred after plan end date")
                )
