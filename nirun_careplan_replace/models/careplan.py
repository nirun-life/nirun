#  Copyright (c) 2023. NSTDA
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class Careplan(models.Model):
    _inherit = "ni.careplan"

    state = fields.Selection(selection_add=[("replaced", "Replaced")])

    replace_id = fields.Many2one(
        "ni.careplan",
        domain="[('patient_id', '=', patient_id), ('state','=', 'active')]",
    )
    replace_by_ids = fields.One2many("ni.careplan", "replace_id")

    def action_replace_by(self, new_plan):
        for plan in self:
            if plan.state not in ["active", "on-hold"]:
                raise ValidationError(_("Must be active state"))
            if plan.period_start > new_plan.period_start:
                raise ValidationError(_("New plan must not start before old plan"))

            plan.goal_ids.filtered(
                lambda g: g.state not in ["completed", "cancelled"]
            ).action_replace()
            plan.activity_ids.filtered(
                lambda a: a.state == "in-progress"
            ).action_complete()
            plan.write(
                {
                    "state": "replaced",
                    "period_end": new_plan.period_start,
                }
            )

    def action_replace_wizard(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {"default_plan_id": self.id, "default_patient_id": self.patient_id.id}
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan_replace", "careplan_replace_wizard_action"
        )
        return dict(action, context=ctx)
