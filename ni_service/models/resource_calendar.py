#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    service_ids = fields.Many2many(
        "ni.service", "ni_service_event_attendance_rel", "attendance_id", "service_id"
    )

    def action_edit(self):
        self.ensure_one()
        view = {
            "name": self.name,
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
            "view_type": "form",
            "views": [[False, "form"]],
            "context": self.env.context,
        }
        return view
