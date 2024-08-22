#  Copyright (c) 2021-2023 NSTDA
import ast

from odoo import _, api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    medication_dispense_ids = fields.One2many(
        "ni.medication.dispense",
        "encounter_id",
    )
    medication_dispense_count = fields.Integer(compute="_compute_medication_dispense")

    medication_request_ids = fields.One2many(
        "ni.medication.request",
        "encounter_id",
    )
    medication_request_count = fields.Integer(compute="_compute_medication_request")

    @api.depends("medication_request_ids")
    def _compute_medication_request(self):
        for rec in self:
            rec.medication_request_count = len(rec.medication_request_ids)

    @api.depends("medication_dispense_ids")
    def _compute_medication_dispense(self):
        statement = self.env["ni.medication.dispense"].sudo()
        read = statement.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for enc in self:
            enc.medication_dispense_count = data.get(enc.id, 0)

    def action_medication_statement(self):
        action_rec = self.env.ref("ni_medication.ni_medication_statement_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_encounter_id": self.ids[0],
                "search_default_state_active": True,
                "search_default_state_completed": True,
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            }
        )
        action["context"] = ctx
        return action

    def action_dispense(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_patient_id": self.patient_id.id,
                "default_encounter_id": self.id,
                "create": False,
            }
        )
        view = {
            "name": "Medication Dispense",
            "res_model": "ni.medication.dispense",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_mode": "list,kanban,form",
            "context": ctx,
        }
        return view

    def action_view_dispense(self):
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            ._for_xml_id("ni_medication.ni_medication_dispense_action")
        )
        action["display_name"] = _("Dispense")
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        context.update({"create": self.active, "active_test": self.active})
        action["context"] = context
        action["domain"] = [("encounter_id", "=", self.id)]
        return action
