#  Copyright (c) 2025 NSTDA
import ast

from odoo import _, api, fields, models


class Condition(models.Model):
    _inherit = "ni.condition"

    careplan_ids = fields.Many2many(
        "ni.careplan",
        "ni_careplan_condition",
        "condition_id",
        "plan_id",
        context={"default_patient_id": "patient_id"},
        domain="[('patient_id', '=', patient_id)]",
    )
    careplan_count = fields.Integer(compute="_compute_careplan_count")

    template_id = fields.Many2one(
        "ni.careplan.template", domain="[('condition_code_ids', 'parent_of', code_id)]"
    )

    def action_view_careplan(self):
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            ._for_xml_id("ni_careplan.ni_careplan_action")
        )
        action["display_name"] = _("%(name)s's Careplan", name=self.name)
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        context.update(
            {
                "default_patient_id": self.patient_id.id,
                "default_template_id": self.template_id.id,
                "default_condition_ids": [fields.Command.link(self.id)],
            }
        )
        action["context"] = context
        action["domain"] = [("condition_ids", "in", self.ids)]
        return action

    def action_new_careplan(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_encounter_id": self.encounter_id.id,
                "default_patient_id": self.patient_id.id,
                "default_template_id": self.template_id.id,
                "default_condition_ids": [fields.Command.link(self.id)],
            }
        )
        view = {
            "name": self.env["ni.careplan"]._description,
            "res_model": "ni.careplan",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_type": "form",
            "views": [[False, "form"]],
            "context": ctx,
        }
        return view

    @api.depends("careplan_ids")
    def _compute_careplan_count(self):
        for rec in self:
            rec.careplan_count = len(rec.careplan_ids)


class Diagnosis(models.Model):
    _inherit = "ni.encounter.diagnosis"

    def action_view_careplan(self):
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            ._for_xml_id("ni_careplan.ni_careplan_action")
        )
        action["display_name"] = _("%(name)s's Careplan", name=self.name)
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        context.update(
            {
                "default_encounter_id": self.encounter_id.id,
                "default_patient_id": self.patient_id.id,
                "default_template_id": self.template_id.id,
                "default_condition_ids": [fields.Command.link(self.condition_id.id)],
            }
        )
        action["context"] = context
        action["domain"] = [("condition_ids", "in", self.mapped("condition_id").ids)]
        return action

    def action_new_careplan(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_encounter_id": self.encounter_id.id,
                "default_patient_id": self.patient_id.id,
                "default_template_id": self.template_id.id,
                "default_condition_ids": [fields.Command.link(self.condition_id.id)],
            }
        )
        plan = self.env["ni.careplan"].create(
            {
                "encounter_id": self.encounter_id.id,
                "patient_id": self.patient_id.id,
                "template_id": self.template_id.id,
                "category_id": self.template_id.category_id.id or None,
                "condition_ids": [fields.Command.link(self.condition_id.id)],
            }
        )
        plan.apply_template()

        view = {
            "name": self.env["ni.careplan"]._description,
            "res_model": "ni.careplan",
            "res_id": plan.id,
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_type": "form",
            "views": [[False, "form"]],
            "context": ctx,
        }
        self.template_id = None
        return view

    @api.onchange("template_id")
    def _onchange_template_id(self):
        for rec in self.filtered_domain([("template_id", "!=", False)]):
            plan = rec.careplan_ids.filtered_domain(
                [
                    ("template_id", "=", rec.template_id.id),
                    ("state", "in", ["draft", "active"]),
                ]
            )
            if plan:
                return {
                    "warning": {
                        "title": _("Warning!"),
                        "message": _(
                            "Careplan '%s' was already drafted or currently active for this patient"
                        )
                        % (self.template_id.name),
                    }
                }
