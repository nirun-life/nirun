#  Copyright (c) 2023. NSTDA
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def _get_next_identifier(plan):
    regex = re.compile(r"^(.*)/(\d{2})$")
    if regex.match(plan.identifier):
        split = plan.identifier.split("/")
        num = int(split[-1]) + 1
        split[-1] = f"{num:02d}"
        return "/".join(split)
    return f"{plan.identifier}/02"


class CareplanReplaceWizard(models.TransientModel):
    _name = "ni.careplan.replace.wizard"
    _inherit = ["period.mixin"]
    _description = "Replace Careplan Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CareplanReplaceWizard, self).default_get(fields)
        if (not fields or "plan_id" in fields) and "plan_id" not in res:
            if self.env.context.get("active_id"):
                res["plan_id"] = self.env.context["active_id"]
        if "plan_id" in res and "period_start" in fields:
            plan = self.env["ni.careplan"].browse(res["plan_id"])
            date = plan.period_end or plan.period_start
            res["period_start"] = date
            res["period_end"] = date
        return res

    patient_id = fields.Many2one("ni.patient")
    plan_id = fields.Many2one(
        "ni.careplan", "Replace Plan", domain="[('patient_id', '=?', patient_id)]"
    )
    plan_period_start = fields.Date(related="plan_id.period_start")
    plan_period_end = fields.Date(related="plan_id.period_end")

    period_start = fields.Date(required=True)

    @api.constrains("plan_id", "period_start")
    def check_period(self):
        if (
            self.plan_period_start > self.period_start
            or self.plan_period_end
            and self.plan_period_end > self.period_start
        ):
            raise ValidationError(_("Start of new plan must occur after the old one"))

    def action_replace(self):
        plan_data = self.plan_id.copy_data()
        plan_data[0].update(
            {
                "identifier": _get_next_identifier(self.plan_id),
                "replace_id": self.plan_id.id,
                "period_start": self.period_start,
                "period_end": self.period_end,
            }
        )
        plan = self.env["ni.careplan"].create(plan_data)
        self.plan_id.action_replace_by(plan)
        return True
