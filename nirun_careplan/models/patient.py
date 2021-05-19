#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    careplan_ids = fields.One2many("ni.careplan", "patient_id", "Careplan(s)")
    careplan_id = fields.Many2one(
        "ni.careplan", "Careplan", compute="_compute_careplan_activity"
    )
    careplan_activity_count = fields.Integer(
        "Activities", compute="_compute_careplan_activity", sudo_compute=True
    )

    @api.depends("careplan_ids")
    def _compute_careplan_activity(self):
        activities = self.env["ni.careplan.activity"].read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["patient_id"]
        )
        result = {
            data["patient_id"][0]: data["patient_id_count"] for data in activities
        }
        for plan in self:
            plan.careplan_id = plan.careplan_ids[0] if plan.careplan_ids else None
            plan.careplan_activity_count = result.get(plan.id, 0)

    # -------------
    # Actions
    # -------------

    def open_careplan_activity(self):
        self.ensure_one()
        patient = self[0]
        if len(patient.careplan_ids) == 1:
            return patient.careplan_ids[0].open_activity()
        else:
            return patient.open_all_careplan_activity()

    def open_all_careplan_activity(self):
        self.ensure_one()
        patient = self[0]
        ctx = dict(self.env.context)
        ctx.update(
            {"search_default_patient_id": patient.id, "default_patient_id": patient.id}
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_activity_action"
        )
        return dict(action, context=ctx)
