#  Copyright (c) 2021-2023 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Discharge(models.TransientModel):
    _name = "ni.encounter.discharge.wizard"
    _description = "Discharge"

    encounter_id = fields.Many2one("ni.encounter", required=True)
    encounter_start = fields.Datetime(related="encounter_id.period_start")
    patient_id = fields.Many2one(related="encounter_id.patient_id", required=True)
    discharge_status_id = fields.Many2one(
        "ni.encounter.discharge.status", "Status", required=True
    )
    discharge_disposition_id = fields.Many2one(
        "ni.encounter.discharge.disposition", "Disposition", required=True
    )
    discharge_disposition_referral = fields.Boolean(
        related="discharge_disposition_id.referral"
    )
    discharge_date = fields.Datetime(
        default=lambda self: fields.Datetime.now(), required=True
    )
    discharge_partner_id = fields.Many2one(
        "res.partner", "Destination", domain=[("patient", "=", False)]
    )
    deceased = fields.Boolean(related="discharge_disposition_id.deceased", store=True)
    decease_date = fields.Date()
    note = fields.Text()

    @api.onchange("discharge_status_id")
    def _onchange_discharge_status_id(self):
        res = {}
        if self.discharge_status_id and self.discharge_status_id.disposition_ids:
            res["domain"] = {
                "discharge_disposition_id": [
                    ("id", "in", self.discharge_status_id.disposition_ids.ids)
                ]
            }
            if (
                self.discharge_disposition_id
                and self.discharge_disposition_id
                not in self.discharge_status_id.disposition_ids
            ):
                self.discharge_disposition_id = (
                    self.discharge_status_id.disposition_ids[0]
                )
                res["value"] = {
                    "discharge_disposition_id": self.discharge_status_id.disposition_ids.ids[
                        0
                    ]
                }
            return res
        else:
            res["domain"] = {"discharge_disposition_id": "[('status_ids','=', False)]"}
            if self.discharge_disposition_id.status_ids:
                res["value"] = {"discharge_disposition_id": False}
            return res

    @api.onchange("discharge_disposition_id")
    def _onchange_discharge_disposition_id(self):
        if (
            self.discharge_disposition_id.status_ids
            and self.discharge_status_id not in self.discharge_disposition_id.status_ids
        ):
            self.discharge_status_id = self.discharge_disposition_id.status_ids[0]

    @api.constrains("decease_date")
    def check_decease_date(self):
        for rec in self:
            if rec.deceased and not rec.decease_date:
                raise UserError(_("Decease date should not be null"))
            if rec.decease_date and rec.decease_date < rec.encounter_start:
                raise UserError(_("Decease date should not before encounter start"))
            if rec.decease_date and rec.decease_date > fields.Date.today():
                raise UserError(_("Decease date should not be in the future"))

    @api.constrains("discharge_date")
    def check_discharge_date(self):
        for rec in self:
            if rec.discharge_date < rec.encounter_start:
                raise UserError(_("Discharge date should not before encounter start"))
            if rec.discharge_date.date() > fields.Date.today():
                raise UserError(_("Discharge date should not be in the future"))

    def discharge(self):
        self.encounter_id.action_close(
            {
                "state": "finished",
                "period_end": self.discharge_date,
                "discharge_disposition_id": self.discharge_disposition_id.id,
                "discharge_status_id": self.discharge_status_id.id,
                "discharge_partner_id": self.discharge_partner_id.id or None,
                "discharge_note": self.note,
            }
        )
        if self.deceased:
            self.patient_id.write(
                {"deceased": True, "deceased_date": self.decease_date}
            )
