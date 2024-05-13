#  Copyright (c) 2024 NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    resource_calendar_id = fields.Many2one("resource.calendar", check_company=True)
    service_ids = fields.Many2many(
        "ni.service", domain="[('company_id', '=', company_id)]"
    )
    service_resource_ids = fields.One2many(
        "ni.encounter.service.resource", "encounter_id"
    )

    @api.onchange("class_id")
    def _onchange_class_id(self):
        for rec in self:
            if rec.class_id.service_ids:
                rec.service_ids = rec.class_id.service_ids

    def action_generate_service_resource(self):
        self.ensure_one()
        attendance_ids = self.env["resource.calendar.attendance"].search(
            [
                ("calendar_id", "=", self.resource_calendar_id.id),
                ("dayofweek", "=", self.period_start.weekday()),
            ]
        )
        service = self.env["ni.service"].search(
            [
                ("attendance_ids", "in", attendance_ids.ids),
                "|",
                ("date", "=", False),
                ("date", "=", fields.Date.today()),
            ]
        )
        dict = {}
        for attendance in attendance_ids:
            service = service.filtered_domain([("attendance_ids", "=", attendance.id)])
            if service:
                dict.update({attendance.id: service[0].id})

        self.service_resource_ids = [
            fields.Command.create(
                {
                    "encounter_id": self.id,
                    "attendance_id": attendance_id,
                    "service_id": service_id,
                }
            )
            for attendance_id, service_id in dict.items()
        ]


class EncounterServiceResource(models.Model):
    _name = "ni.encounter.service.resource"
    _description = "Service Resource"
    _order = "sequence"

    sequence = fields.Integer(related="attendance_id.sequence")
    encounter_id = fields.Many2one("ni.encounter", required=True, ondelete="cascade")
    encounter_date = fields.Date(related="encounter_id.period_start_date")
    resource_calendar_id = fields.Many2one(related="encounter_id.resource_calendar_id")

    attendance_id = fields.Many2one(
        "resource.calendar.attendance",
        required=True,
        domain="[('calendar_id','=?', resource_calendar_id)]",
    )
    service_id = fields.Many2one(
        "ni.service",
        required=True,
        domain="[('attendance_ids', '=', attendance_id), '|', ('date', '=', False), ('date', '=', encounter_date)]",
        check_company=True,
    )

    _sql_constraints = [
        (
            "encounter_attendance_uniq",
            "unique (encounter_id, attendance_id)",
            "The attendance time must be unique!",
        ),
    ]


class EncounterClass(models.Model):
    _inherit = "ni.encounter.class"

    service_ids = fields.Many2many("ni.service", help="Default Service")
