#  Copyright (c) 2021-2023. NSTDA

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
        "ni.patient",
        related="careplan_id.patient_id",
    )
    encounter_id = fields.Many2one(
        "ni.encounter",
        related="careplan_id.encounter_id",
    )
    manager_id = fields.Many2one(
        string="Care Manager",
        related="careplan_id.manager_id",
        readonly=True,
    )

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

    def _name_get(self):
        act = self
        name = super(CareplanActivity, self)._name_get()
        if self._context.get("show_timing") and act.timing_id:
            name = "{}, {}".format(name, act.timing_id.name)
        return name

    @api.depends("name", "timing_id")
    def _compute_display_name(self):
        diff = dict(show_timing=None, show_patient=None, show_state=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    @api.model
    def create(self, vals):
        context = dict(self.env.context)
        if vals.get("careplan_id") and not context.get("default_careplan_id"):
            # set default_careplan_id for create next activity
            context["default_careplan_id"] = vals.get("careplan_id")
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

    @api.onchange("service_request_id")
    def _onchange_service_request_id(self):
        for rec in self:
            req = rec.service_request_id
            if req:
                if rec.service_id != req.service_id:
                    rec.service_id = req.service_id
                if req.service_timing_id:
                    rec.timing_id = req.service_timing_id.timing_id
                elif req.service_time_id:
                    rec.timing_id = req.service_time_id.to_timing().timing_id
