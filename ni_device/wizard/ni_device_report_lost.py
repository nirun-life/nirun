from odoo import _, fields, models


class DeviceReportLostWizard(models.TransientModel):
    _name = "ni.device.report.lost.wizard"
    _description = "Report Device Lost"

    device_id = fields.Many2one(
        "ni.device",
        string="Device",
        required=True,
        readonly=True,
    )
    note = fields.Text(string="Note")

    action_type = fields.Selection(
        [
            ("lost", "Report Lost"),
            ("found", "Report Found"),
        ],
        required=True,
        readonly=True,
    )

    note = fields.Text(string="Note")

    def action_confirm(self):
        self.ensure_one()
        device = self.device_id.sudo()
        today = fields.Date.context_today(self)

        if self.action_type == "lost":
            device.write(
                {
                    "availability_status": "lost",
                    "lost_date": today,
                }
            )
            body = "<b>‼️ %s</b>" % _("Device reported as LOST")
        else:
            device.write(
                {
                    "availability_status": "available",
                    "lost_date": False,
                }
            )

            body = "<b>✅ %s</b>" % _("Device found and returned to available")

        if self.note:
            body += "<br/><i>Note:</i><br/>%s" % self.note

        device.message_post(
            body=body,
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )

        return {"type": "ir.actions.act_window_close"}
