#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class FlagRecommendation(models.Model):
    _name = "ni.flag.recommendation"
    _description = "Flag Recommendation"
    _inherit = ["ni.patient.res"]
    _order = "create_date DESC, id DESC"
    _check_period_start = False
    _sql_constraints = [
        (
            "ni_flag_recommendation_rule_source_uniq",
            "unique(rule_id, source_observation_id)",
            "A rule can only recommend once per source observation.",
        ),
    ]

    name = fields.Char(required=True)
    flag_code_id = fields.Many2one("ni.flag.code", required=True, ondelete="restrict")
    rule_id = fields.Many2one(
        "ni.flag.recommendation.rule", required=True, ondelete="cascade"
    )
    source_observation_id = fields.Many2one(
        "ni.observation", required=True, ondelete="cascade", index=True
    )
    reason = fields.Text()
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("dismissed", "Dismissed"),
            ("auto_applied", "Auto Applied"),
        ],
        required=True,
        default="pending",
        index=True,
    )
    flag_id = fields.Many2one("ni.flag", ondelete="set null")

    def action_accept(self):
        for rec in self:
            conflicts = rec._conflicting_active_flags()
            if conflicts and not self.env.context.get("force_conflict_resolution"):
                view = self.env.ref("ni_flag.ni_flag_conflict_wizard_view_form")
                wizard = self.env["ni.flag.conflict.wizard"].create(
                    {"recommendation_id": rec.id}
                )
                return {
                    "name": "Resolve Conflicting Flags",
                    "type": "ir.actions.act_window",
                    "res_model": "ni.flag.conflict.wizard",
                    "view_mode": "form",
                    "res_id": wizard.id,
                    "views": [(view.id, "form")],
                    "target": "new",
                }
            conflicts.action_inactive()
            rec._apply_flag("recommendation")
            rec.write({"state": "accepted"})
        return True

    def action_dismiss(self):
        self.write({"state": "dismissed"})
        return True

    def action_auto_apply(self):
        for rec in self:
            rec._conflicting_active_flags().action_inactive()
            rec._apply_flag("auto_rule")
            rec.write({"state": "auto_applied"})
        return True

    def _apply_flag(self, origin):
        Flag = self.env["ni.flag"]
        for rec in self:
            flag = rec._active_matching_flag()
            if not flag:
                flag = Flag.create(rec._flag_values(origin))
            else:
                flag.write(
                    {
                        "origin": origin,
                        "source_observation_id": rec.source_observation_id.id,
                        "recommendation_id": rec.id,
                    }
                )
            rec.write({"flag_id": flag.id})
        return True

    def name_get(self):
        return [(rec.id, rec.flag_code_id.name or rec.name) for rec in self]

    def _flag_values(self, origin):
        self.ensure_one()
        return {
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "code_id": self.flag_code_id.id,
            "origin": origin,
            "source_observation_id": self.source_observation_id.id,
            "recommendation_id": self.id,
        }

    def _active_matching_flag(self):
        self.ensure_one()
        domain = [
            ("patient_id", "=", self.patient_id.id),
            ("code_id", "=", self.flag_code_id.id),
            ("status", "=", "active"),
        ]
        if self.encounter_id:
            domain.append(("encounter_id", "=", self.encounter_id.id))
        else:
            domain.append(("encounter_id", "=", False))
        return self.env["ni.flag"].search(domain, limit=1)

    def _conflicting_active_flags(self):
        self.ensure_one()
        conflict_codes = self.flag_code_id.conflict_code_ids
        if not conflict_codes:
            return self.env["ni.flag"]
        domain = [
            ("patient_id", "=", self.patient_id.id),
            ("code_id", "in", conflict_codes.ids),
            ("status", "=", "active"),
        ]
        if self.encounter_id:
            domain.append(("encounter_id", "=", self.encounter_id.id))
        else:
            domain.append(("encounter_id", "=", False))
        return self.env["ni.flag"].search(domain)
