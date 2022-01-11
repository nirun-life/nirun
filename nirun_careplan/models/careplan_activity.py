#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class CareplanActivity(models.Model):
    _name = "ni.careplan.activity"
    _description = "Careplan Activity"
    _inherit = [
        "ni.careplan.activity.base",
        "mail.thread",
        "mail.activity.mixin",
        "period.mixin",
        "ni.timing.mixin",
    ]
    _check_company_auto = True

    patient_id = fields.Many2one(
        "ni.patient", related="careplan_id.patient_id", store=True
    )
    encounter_id = fields.Many2one("ni.encounter", related="careplan_id.encounter_id",)
    manager_id = fields.Many2one(
        string="Care Manager", related="careplan_id.manager_id", readonly=True,
    )
    careplan_goal_ids = fields.One2many(related="careplan_id.goal_ids")
    goal_id = fields.Many2one("ni.careplan.goal", index=True, ondelete="set null")

    kanban_state = fields.Selection(
        [("normal", "Grey"), ("done", "Green"), ("blocked", "Red")],
        string="Kanban State",
        copy=False,
        default="normal",
        required=True,
    )
    assignee_id = fields.Many2one(
        "hr.employee",
        string="Assigned to",
        index=True,
        tracking=True,
        check_company=True,
    )
    assignee_uid = fields.Many2one(
        related="assignee_id.user_id", string="Assigned User", store=True
    )
    assign_date = fields.Datetime(copy=False, readonly=True)
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        context = dict(self.env.context)
        if vals.get("careplan_id") and not context.get("default_careplan_id"):
            # set default_careplan_id for create next activity
            context["default_careplan_id"] = vals.get("careplan_id")
        if (
            vals.get("period_start")
            and fields.Date.to_date(vals.get("period_start")) >= fields.Date.today()
        ):
            vals["state"] = "in-progress"
        return super().create(vals)

    def write(self, vals):
        now = fields.Datetime.now()
        if vals.get("state"):
            if "kanban_state" not in vals:
                vals["kanban_state"] = "normal"
        if vals.get("assignee_id") and "assign_date" not in vals:
            vals["assign_date"] = now
        return super().write(vals)

    @api.onchange("careplan_id")
    def _onchange_careplan(self):
        for rec in self:
            if rec.careplan_id:
                rec.write(
                    {
                        "period_start": rec.careplan_id.period_start,
                        "period_end": rec.careplan_id.period_end,
                    }
                )

    def copy_timing_form_template(self):
        for rec in self:
            if rec.timing_tmpl_id:
                rec.timing_id = rec.timing_tmpl_id.to_timing().id
