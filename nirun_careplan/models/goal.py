#  Copyright (c) 2022-2023. NSTDA
import pprint

from odoo import api, fields, models


class Goal(models.Model):
    _inherit = "ni.goal"

    @api.model
    def default_get(self, fields):
        res = super(Goal, self).default_get(fields)
        if "careplan_id" in fields and "careplan_id" not in res:
            if (
                self.env.context.get("active_id")
                and self.env.context.get("active_model") == "ni.careplan"
            ):
                res["careplan_id"] = self.env.context["active_id"]

        if res.get("careplan_id"):
            plan = self.env["ni.careplan"].browse(res.get("careplan_id"))
            if "patient_id" in fields and "patient_id" not in res:
                res["patient_id"] = plan.patient_id.id
            if "encounter_id" in fields and "encounter_id" not in res:
                res["encounter_id"] = plan.encounter_id.id
            if "period_start" in fields and "period_start" not in res:
                res["period_start"] = plan.period_start
            if "period_end" in fields and "period_end" not in res:
                res["period_end"] = plan.period_end
        pprint.pprint(res)
        return res

    careplan_id = fields.Many2one(
        "ni.careplan", required=False, index=True, ondelete="cascade", copy=False
    )

    @api.onchange("careplan_id")
    def _onchange_careplan_id(self):
        for rec in self:
            plan = rec.careplan_id
            if plan and (
                rec.encounter_id != plan.encounter_id
                or rec.patient_id != plan.patient_id
            ):
                rec.update(
                    {
                        "encounter_id": plan.encounter_id.id,
                        "patient_id": plan.patient_id.id,
                    }
                )
