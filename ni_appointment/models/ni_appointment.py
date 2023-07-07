#  Copyright (c) 2023 NSTDA

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class Appointment(models.Model):
    _name = "ni.appointment"
    _description = "Appointment"
    _inherit = ["ni.workflow.request.mixin", "ni.identifier.mixin"]
    _inherits = {"calendar.event": "event_id"}
    _parent_store = True

    patient_name = fields.Char(related="patient_id.name")
    patient_identifier = fields.Char(related="patient_id.identifier")

    event_id = fields.Many2one("calendar.event", index=True, ondelete="cascade")
    hide_next = fields.Boolean(compute="_compute_hide_next")
    next_days = fields.Integer()
    next_weeks = fields.Integer()

    parent_id = fields.Many2one(
        "ni.appointment", "Previous Appointment", index=True, ondelete="restrict"
    )
    parent_path = fields.Char(index=True, unaccent=False)

    type_id = fields.Many2one(
        "ni.appointment.type",
        required=True,
        default=lambda self: self.env.ref("ni_appointment.type_routine"),
    )

    reason_ids = fields.Many2many(
        "ni.encounter.reason",
        "ni_appointment_reason",
        "appointment_id",
        "reason_id",
    )
    reason_condition_ids = fields.Many2many(
        "ni.condition",
        "ni_appointment_condition",
        "appointment_id",
        "condition_id",
        domain="[('encounter_id', '=', encounter_id)]",
    )

    performer_id = fields.Many2one("hr.employee", required=True)
    department_id = fields.Many2one(
        "hr.department", related="performer_id.department_id"
    )
    instruction_ids = fields.Many2many(
        "ni.appointment.instruction",
        "ni_appointment_patent_instruction",
        "appointment_id",
        "instruction_id",
    )

    cancel_reason_id = fields.Many2one("ni.appointment.cancel.reason", tracking=True)
    cancel_note = fields.Text(tracking=True)
    cancel_date = fields.Datetime()
    cancel_uid = fields.Many2one("res.users", "Cancelled by")

    @api.depends("create_date")
    def _compute_hide_next(self):
        for rec in self:
            rec.hide_next = (
                self.create_date.date() or fields.date.today()
            ) != fields.date.today()

    @api.onchange("next_days")
    def _onchange_next_day(self):
        if self.next_days > 0:
            self.next_weeks = 0
            self._update_start_next(days=self.next_days)

    @api.onchange("next_weeks")
    def _onchange_next_week(self):
        if self.next_weeks > 0:
            self.next_days = 0
            self._update_start_next(days=7 * self.next_weeks)

    def _update_start_next(self, days=0):
        time = self.start.time()
        date = fields.Datetime.now().date() + relativedelta(days=days)
        self.start = fields.Datetime.to_datetime(datetime.combine(date, time))

    @api.onchange("performer_id")
    def _onchange_performer_id(self):
        for rec in self:
            if rec.performer_id.work_contact_id:
                rec.location = rec.performer_id.work_location_id.name

    def name_get(self):
        return [(appointment.id, appointment._get_name()) for appointment in self]

    def _get_name(self):
        appointment = self
        name = "{} {}".format(appointment.name, appointment.start.date())
        if self.state == "revoked":
            name = "{}  ❌".format(name)
        elif self.state == "completed":
            name = "{}  ✅".format(name)
        if self._context.get("show_employee"):
            name = "{}\n{}".format(name, self.performer_id.name)
        return name

    def write(self, vals):
        if "cancel_reason_id" in vals or "cancel_note" in vals:
            if "cancel_date" not in vals:
                vals["cancel_date"] = fields.Datetime.now()
            if "cancel_uid" not in vals:
                vals["cancel_uid"] = self.env.uid
        return super().write(vals)

    def unlink(self):
        result = (
            self.env["calendar.event"]
            .search([("id", "in", self.event_id.ids)])
            .unlink()
        )
        result &= super().unlink()
        return result

    def action_print(self):
        return self.env.ref("ni_appointment.action_report_appointment").report_action(
            self.ids
        )

    def action_active(self):
        self._action_active()

    def _action_active(self):
        self.write({"state": "active"})
        for rec in self:
            attendee = []
            if rec.patient_id.partner_id not in rec.partner_ids:
                attendee += [fields.Command.link(rec.patient_id.partner_id.id)]

            employee_partner_ids = [
                rec.performer_id.user_partner_id,
                rec.performer_id.work_contact_id,
                rec.performer_id.address_home_id,
            ]
            for partner_id in employee_partner_ids:
                if partner_id and partner_id not in rec.partner_ids:
                    attendee += [fields.Command.link(partner_id.id)]
                    break

            if attendee:
                rec.write({"partner_ids": attendee})

    def action_encounter(self):
        action = {
            "type": "ir.actions.act_window",
            "res_model": "ni.encounter",
            "views": [[False, "form"]],
            "context": {
                "default_patient_id": self.patient_id.id,
                "default_appointment_id": self.id,
            },
        }
        encounter = self.env["ni.encounter"].search([("appointment_id", "=", self.id)])
        if encounter:
            action.update({"res_id": encounter.id})
        return action

    def action_cancel_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Appointment Cancellation"),
            "res_model": "ni.appointment.cancel.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_appointment_id": self.id},
            "views": [[False, "form"]],
        }

    def action_revoked(self):
        self.filtered_domain([("state", "in", "in-progress")]).write(
            {"state": "revoked", "cancel_date": fields.Datetime.now()}
        )

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive item."))
