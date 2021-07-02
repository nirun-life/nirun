#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    careplan_ids = fields.One2many(
        "ni.careplan", "patient_id", "Careplan(s)", groups="nirun_careplan.group_user"
    )
    careplan_count = fields.Integer(
        compute="_compute_careplan_count", groups="nirun_careplan.group_user"
    )
    careplan_activity_count = fields.Integer(
        "Activities", compute="_compute_careplan_activity"
    )

    @api.depends("careplan_ids")
    def _compute_careplan_count(self):
        for rec in self:
            rec.careplan_count = len(rec.careplan_ids)

    def _compute_careplan_activity(self):
        activities = self.env["ni.careplan.activity"].sudo()
        result = activities.read_group(
            domain=[
                ("patient_id", "in", self.ids),
                ("state", "in", ["scheduled", "in-progress"]),
            ],
            fields=["patient_id"],
            groupby=["patient_id"],
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in result}
        for patient in self:
            patient.careplan_activity_count = data.get(patient.id, 0)

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
