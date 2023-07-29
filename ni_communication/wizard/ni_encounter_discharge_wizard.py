#  Copyright (c) 2021-2023 NSTDA
from random import randint

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class Discharge(models.TransientModel):
    _inherit = "ni.encounter.discharge.wizard"

    @api.model
    def default_get(self, fields):
        if self.env.context.get("default_encounter_id"):
            suggest = self.env.ref("ni_communication.categ_suggestion")
            com = self.env["ni.communication"].search(
                [
                    ("encounter_id", "=", self.env.context["default_encounter_id"]),
                    ("category_id", "=", suggest.id),
                ],
                limit=1,
            )
            self = self.with_context(default_discharge_communication_id=com.id)
        return super(Discharge, self).default_get(fields)

    discharge_communication_id = fields.Many2one(
        "ni.communication", domain="[('encounter_id', '=', encounter_id)]"
    )
    discharge_communication_content_ids = fields.Many2many(
        related="discharge_communication_id.content_ids", readonly=False
    )
    suggest_content_ids = fields.Many2many("ni.communication.content")

    def discharge(self):
        super(Discharge, self).discharge()

        if not self.discharge_communication_id:
            now = fields.Datetime.now()
            start = now - relativedelta(minutes=randint(2, 3), seconds=randint(0, 60))
            vals = {
                "encounter_id": self.encounter_id.id,
                "patient_id": self.patient_id.id,
                "category_id": self.env.ref("ni_communication.categ_suggestion").id,
                "content_ids": [fields.Command.set(self.suggest_content_ids.ids)],
                "period_start": start,
                "period_end": now,
                "sender_employee_id": self.env.user.employee_id.id or None,
                "recipient_ids": [fields.Command.link(self.patient_id.partner_id.id)],
            }
            self.discharge_communication_id = self.env["ni.communication"].create(vals)

        self.encounter_id.write(
            {
                "discharge_communication_id": self.discharge_communication_id.id,
            }
        )
