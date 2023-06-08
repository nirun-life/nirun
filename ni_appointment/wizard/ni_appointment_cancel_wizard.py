from odoo import fields, models


class AppointmentCancelWizard(models.TransientModel):
    _name = "ni.appointment.cancel.wizard"
    _description = "Appointment Cancellation Wizard"

    appointment_id = fields.Many2one("ni.appointment", required=True)

    cancel_reason_id = fields.Many2one("ni.appointment.cancel.reason", required=True)
    cancel_note = fields.Text()

    def action_cancel(self):
        self.appointment_id.write(
            {
                "cancel_reason_id": self.cancel_reason_id.id,
                "cancel_note": self.cancel_note,
                "state": "revoked",
            }
        )
