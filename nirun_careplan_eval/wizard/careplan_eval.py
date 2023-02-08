#  Copyright (c) 2023. NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CareplanEvalWizard(models.TransientModel):
    _name = "ni.careplan.eval.wizard"
    _description = "Careplan Evaluation Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CareplanEvalWizard, self).default_get(fields)
        if (not fields or "careplan_id" in fields) and "careplan_id" not in res:
            if self.env.context.get("active_id"):
                res["careplan_id"] = self.env.context["active_id"]
        return res

    patient_id = fields.Many2one("ni.patient")
    careplan_id = fields.Many2one(
        "ni.careplan",
        "Care Plan",
        required=True,
        domain="[('patient_id', '=?', patient_id)]",
    )
    period_start = fields.Date(related="careplan_id.period_start")
    period_end = fields.Date(related="careplan_id.period_end")

    state = fields.Selection(related="careplan_id.state")
    mode = fields.Selection(
        [("pre", "Pre-Evaluation"), ("post", "Post-Evaluation")],
        default="pre",
        require=True,
    )
    pre_eval = fields.Text(
        "Pre-Evaluation",
        readonly=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
    )
    pre_eval_date = fields.Datetime(
        readonly=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
        default=fields.Datetime.now,
    )
    post_eval = fields.Text(
        "Post-Evaluation",
        readonly=True,
        states={"completed": [("readonly", False)]},
    )
    post_eval_date = fields.Datetime(
        readonly=True,
        states={"completed": [("readonly", False)]},
        default=fields.Datetime.now,
    )

    @api.onchange("careplan_id")
    def _onchange_careplan_id(self):
        if self.careplan_id:
            plan = self.careplan_id
            self.update(
                {
                    "pre_eval": plan.pre_eval,
                    "pre_eval_date": plan.pre_eval_date,
                    "post_eval": plan.post_eval,
                    "post_eval_date": plan.post_eval_date,
                }
            )

    @api.constrains("mode", "pre_eval", "pre_eval_date", "post_eval", "post_eval_date")
    def check_eval(self):
        for rec in self:
            mode = rec.mode
            if not rec.mapped("%s_eval" % mode) or not rec.mapped(
                "%s_eval_date" % mode
            ):
                raise ValidationError(_("%s and it date must be provided" % mode))

    def action_eval(self):
        if self.mode == "post" and self.state != "completed":
            return False

        f = ["%s_eval" % self.mode, "%s_eval_date" % self.mode]
        return self.careplan_id.write(
            {
                f[0]: getattr(self, f[0]),
                f[1]: getattr(self, f[1]),
            }
        )
