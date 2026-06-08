#  Copyright (c) 2026 NSTDA
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class Encounter(models.Model):
    _name = "ni.encounter"
    _inherit = "ni.encounter"

    flag_ids = fields.One2many(
        "ni.flag",
        "encounter_id",
        string="Flag Records",
        check_company=True,
        help="Prospective warnings of potential issues when providing care to the patient.",
    )
    patient_flag_code_ids = fields.Many2many(
        "ni.flag.code",
        compute="_compute_patient_flag_code_ids",
        inverse="_inverse_patient_flag_code_ids",
        string="Patient Flags",
        help="Patient-wide flags that stay visible across all encounters for this patient.",
    )
    encounter_flag_code_ids = fields.Many2many(
        "ni.flag.code",
        compute="_compute_encounter_flag_code_ids",
        inverse="_inverse_encounter_flag_code_ids",
        string="Encounter Flags",
        help="Flags that apply only to this encounter and do not carry to other visits.",
    )
    active_flag_code_ids = fields.Many2many(
        "ni.flag.code",
        compute="_compute_active_flag_code_ids",
        string="Active Flags",
        search="_search_active_flag_code_ids",
    )
    pending_flag_recommendation_count = fields.Integer(
        compute="_compute_pending_flag_recommendation_count",
        search="_search_pending_flag_recommendation_count",
    )

    @api.depends(
        "patient_id.flag_ids.status",
        "patient_id.flag_ids.code_id",
        "patient_id.flag_ids.encounter_id",
    )
    def _compute_patient_flag_code_ids(self):
        for rec in self:
            active = rec.patient_id.flag_ids.filtered(
                lambda f: f.status == "active" and not f.encounter_id
            )
            rec.patient_flag_code_ids = active.mapped("code_id")

    def _inverse_patient_flag_code_ids(self):
        Flag = self.env["ni.flag"]
        for rec in self:
            active = rec.patient_id.flag_ids.filtered(
                lambda f: f.status == "active" and not f.encounter_id
            )
            current_codes = active.mapped("code_id")
            to_add = rec.patient_flag_code_ids - current_codes
            to_remove = active.filtered(
                lambda f: f.code_id not in rec.patient_flag_code_ids
            )
            for code in to_add:
                Flag.create({"patient_id": rec.patient_id.id, "code_id": code.id})
            to_remove.action_inactive()

    @api.depends("flag_ids.status", "flag_ids.code_id")
    def _compute_encounter_flag_code_ids(self):
        for rec in self:
            active = rec.flag_ids.filtered(lambda f: f.status == "active")
            rec.encounter_flag_code_ids = active.mapped("code_id")

    def _inverse_encounter_flag_code_ids(self):
        Flag = self.env["ni.flag"]
        for rec in self:
            active = rec.flag_ids.filtered(lambda f: f.status == "active")
            current_codes = active.mapped("code_id")
            to_add = rec.encounter_flag_code_ids - current_codes
            to_remove = active.filtered(
                lambda f: f.code_id not in rec.encounter_flag_code_ids
            )
            for code in to_add:
                Flag.create(
                    {
                        "patient_id": rec.patient_id.id,
                        "encounter_id": rec.id,
                        "code_id": code.id,
                    }
                )
            to_remove.action_inactive()

    @api.depends("patient_flag_code_ids", "encounter_flag_code_ids")
    def _compute_active_flag_code_ids(self):
        for rec in self:
            rec.active_flag_code_ids = (
                rec.patient_flag_code_ids | rec.encounter_flag_code_ids
            )

    def _search_active_flag_code_ids(self, operator, value):
        domain = [("status", "=", "active")]
        if value:
            if operator in ("=", "in"):
                domain.append(
                    ("code_id", "in", value if isinstance(value, list) else [value])
                )
            elif operator in ("!=", "not in"):
                matching = self.env["ni.flag"].search(
                    [
                        ("status", "=", "active"),
                        (
                            "code_id",
                            "in",
                            value if isinstance(value, list) else [value],
                        ),
                    ]
                )
                matching_encounter_ids = set(matching.mapped("encounter_id").ids)
                matching_patient_ids = matching.filtered(
                    lambda rec: not rec.encounter_id
                ).mapped("patient_id")
                if matching_patient_ids:
                    matching_encounter_ids.update(
                        self.env["ni.encounter"]
                        .search([("patient_id", "in", matching_patient_ids.ids)])
                        .ids
                    )
                return [("id", "not in", list(matching_encounter_ids))]
        active_flags = self.env["ni.flag"].search(domain)
        encounter_ids = set(active_flags.mapped("encounter_id").ids)
        patient_ids = active_flags.filtered(lambda rec: not rec.encounter_id).mapped(
            "patient_id"
        )
        if patient_ids:
            encounter_ids.update(
                self.env["ni.encounter"]
                .search([("patient_id", "in", patient_ids.ids)])
                .ids
            )
        if operator in ("!=", "not in") and not value:
            return [("id", "not in", list(encounter_ids))]
        return [("id", "in", list(encounter_ids))]

    def _compute_pending_flag_recommendation_count(self):
        data = self.env["ni.flag.recommendation"].read_group(
            [("encounter_id", "in", self.ids), ("state", "=", "pending")],
            ["encounter_id"],
            ["encounter_id"],
        )
        mapped = {item["encounter_id"][0]: item["encounter_id_count"] for item in data}
        for rec in self:
            rec.pending_flag_recommendation_count = mapped.get(rec.id, 0)

    def _search_pending_flag_recommendation_count(self, operator, value):
        recommendations = self.env["ni.flag.recommendation"].search(
            [("state", "=", "pending"), ("encounter_id", "!=", False)]
        )
        encounter_ids = recommendations.mapped("encounter_id").ids
        if operator in (">", ">=", "!=") and value in (0, False):
            return [("id", "in", encounter_ids)]
        if operator in ("=", "<=", "<") and value in (0, False):
            return [("id", "not in", encounter_ids)]
        return [("id", "in", encounter_ids)]

    def action_flag_recommendations(self):
        self.ensure_one()
        return {
            "name": "Flag Recommendations",
            "type": "ir.actions.act_window",
            "res_model": "ni.flag.recommendation",
            "view_mode": "tree,form",
            "domain": [("encounter_id", "=", self.id)],
            "context": {"search_default_pending": True},
        }

    def action_manage_flags(self):
        self.ensure_one()
        action = self.env.ref("ni_flag.ni_encounter_flag_action").read()[0]
        action["domain"] = [("encounter_id", "=", self.id)]
        action_context = action.get("context")
        context = (
            safe_eval(action_context)
            if isinstance(action_context, str)
            else dict(action_context or {})
        )
        context.update(self.env.context)
        context.update(
            {
                "default_patient_id": self.patient_id.id,
                "default_encounter_id": self.id,
            }
        )
        action["context"] = context
        return action
