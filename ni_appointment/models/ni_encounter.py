#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    appointment_id = fields.Many2one(
        "ni.appointment", help="The appointment that scheduled this encounter"
    )

    next_appointment_ids = fields.One2many(
        "ni.appointment",
        "encounter_id",
        help="The appointments cause by this encounter",
    )
    next_appointment_id = fields.Many2one(
        "ni.appointment", compute="_compute_next_appointment", store=True
    )
    next_appointment_info = fields.Char(compute="_compute_next_appointment")

    @api.depends("next_appointment_ids")
    def _compute_next_appointment(self):
        for rec in self:
            if rec.next_appointment_ids:
                appointment = rec.next_appointment_ids.sorted("start")[0]
                rec.write(
                    {
                        "next_appointment_id": appointment.id,
                        "next_appointment_info": str(appointment.start.date()),
                    }
                )
            else:
                rec.write(
                    {"next_appointment_id": None, "next_appointment_info": _("Make")}
                )

    def action_close(self, vals=None):
        super(Encounter, self).action_close(vals)
        self.filtered_domain(
            [("appointment_id", "!=", False)]
        ).appointment_id.action_complete()

    def action_next_appointment(self):
        followup = self.env.ref("ni_appointment.type_followup")
        action = {
            "name": _("Appointment"),
            "type": "ir.actions.act_window",
            "res_model": "ni.appointment",
            "views": [[False, "form"]],
            "target": "new",
            "context": {
                "default_patient_id": self.patient_id.id,
                "default_encounter_id": self.id,
                "default_type_id": followup.id,
                "default_name": followup.name,
                "default_parent_id": self.appointment_id.id,
            },
        }
        if self.next_appointment_id:
            action.update(
                {
                    "res_id": self.next_appointment_id.id,
                    "name": self.next_appointment_id.name,
                }
            )
        return action

    @property
    def _workflow_request_id(self):
        request = super()._workflow_request_id
        if not request and self.appointment_id:
            request = self.appointment_id.request_id.id
        return request
