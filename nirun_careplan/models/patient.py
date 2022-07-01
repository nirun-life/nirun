#  Copyright (c) 2021 NSTDA
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    careplan_ids = fields.One2many(
        "ni.careplan",
        "patient_id",
        "Careplan(s)",
        groups="nirun_careplan.group_user",
        domain=[("state", "in", ["draft", "active", "on-hold"])],
        check_company=True,
    )
    careplan_count = fields.Integer(
        compute="_compute_careplan_count", groups="nirun_careplan.group_user", default=0
    )
    careplan_activity_count = fields.Integer(
        "Activities",
        compute="_compute_careplan_activity",
        help="Careplan's activity assigned to current user that still active",
        groups="nirun_careplan.group_user",
    )

    @api.depends("careplan_ids")
    def _compute_careplan_count(self):
        careplans = self.env["ni.careplan"].sudo()
        result = careplans.read_group(
            domain=[
                ("patient_id", "in", self.ids),
                ("state", "in", ["draft", "active", "on-hold"]),
            ],
            fields=["patient_id"],
            groupby=["patient_id"],
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in result}
        for patient in self:
            patient.careplan_count = data.get(patient.id, 0)

    def _compute_careplan_activity(self):
        activities = self.env["ni.careplan.activity"].sudo()
        result = activities.read_group(
            domain=[
                ("patient_id", "in", self.ids),
                ("state", "in", ["scheduled", "in-progress"]),
                ("assignee_uid", "=", self.env.uid),
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
    def create_careplan(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "ni.careplan",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_patient_id": self.id,
                "search_default_patient_id": self.id,
            },
        }

    def open_careplan(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx.update(
            {"search_default_patient_id": self.id, "default_patient_id": self.id}
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_action"
        )
        return dict(action, context=ctx)

    def open_careplan_activity(self):
        self.ensure_one()
        patient = self[0]

        if patient.careplan_count == 1:
            return patient.careplan_ids[0].open_activity()
        elif patient.careplan_count > 1:
            return patient._open_all_careplan_activity()
        else:
            return patient.open_careplan()

    def _open_all_careplan_activity(self):
        self.ensure_one()
        patient = self[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": patient.id,
                "default_patient_id": patient.id,
                "default_careplan_id": patient.careplan_ids[0].id,
            }
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_activity_action"
        )
        return dict(action, context=ctx)
