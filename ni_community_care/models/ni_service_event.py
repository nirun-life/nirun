#  Copyright (c) 2024 NSTDA

from odoo import api, fields, models


class ServiceEvent(models.Model):
    _inherit = "ni.service.event"

    @api.model
    def default_get(self, _fields):
        res = super(ServiceEvent, self).default_get(_fields)
        if "service_category_id" in res and "plan_patient_ids" in res:
            categ = self.env["ni.service.category"].browse(res["service_category_id"])
            careplan = self.env["ni.careplan"].search(
                [
                    ("patient_id", "in", res["plan_patient_ids"][0][2]),
                    ("service_category_id", "=", categ.id),
                ]
            )
            if careplan.service_ids:
                res["service_ids"] = [fields.Command.set(careplan.service_ids.ids)]
        return res

    attendance_id = fields.Many2one(required=False)
    patient_type_id = fields.Many2one("ni.patient.type")

    outcome = fields.Html("ผลการให้ความช่วยเหลือ")
    outcome_id = fields.Many2one("ni.service.event.outcome", "ผลการให้ความช่วยเหลือ")
    patient_id = fields.Many2one("ni.patient", store=False)
    service_category_id = fields.Many2one(store=True)

    prediction_id = fields.Many2one("ni.risk.assessment.prediction")
    plan_patient_ids = fields.Many2many(string="ผู้สูงอายุ")

    @api.onchange("patient_type_id", "service_category_id")
    def _onchange_patient_type_id(self):
        if self.patient_type_id:
            domain = [
                ("category_id", "=", self.service_category_id.id),
                "|",
                ("target_type_ids", "=", False),
                ("target_type_ids", "=", self.patient_type_id.id),
            ]
        else:
            domain = [("category_id", "=", self.service_category_id.id)]
        return {"domain": {"service_ids": domain}}
