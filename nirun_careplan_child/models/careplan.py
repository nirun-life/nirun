#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CarePlan(models.Model):
    _inherit = "ni.careplan"

    parent_id = fields.Many2one(
        "ni.careplan",
        string="Part of",
        index=True,
        ondelete="cascade",
        copy=False,
        domain="[('parent_id', '=', False), ('active', '=', True)]",
    )
    child_ids = fields.One2many(
        "ni.careplan",
        "parent_id",
        string="Sub-Care plans",
        domain="[('active', '=', True)]",
    )
    child_count = fields.Integer(compute="_compute_child_count")

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        if self.parent_id:
            self.encounter_id = self.parent_id.encounter_id
            self.patient_id = self.parent_id.patient_id
            self.author_id = self.parent_id.author_id
            self.intent = self.parent_id.intent
            self.period_start = self.parent_id.period_start
            self.period_end = self.parent_id.period_end

    def _compute_child_count(self):
        child = self.env["ni.careplan"].read_group(
            [("parent_id", "in", self.ids)], ["parent_id"], ["parent_id"]
        )
        result = {data["parent_id"][0]: data["parent_id_count"] for data in child}
        for plan in self:
            plan.child_count = result.get(plan.id, 0)

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(
                _("Error! You cannot create recursive careplan.")
            )
        if self.parent_id.parent_id:
            raise models.ValidationError(
                _("Error! You cannot create third deep careplan.")
            )

    def write(self, vals):
        if "active" in vals:
            self.with_context(active_test=False).mapped("child_ids").write(
                {"active": vals["active"]}
            )
        return super().write(vals)

    # -------------
    # Actions
    # -------------
    @api.model
    def open_sub_careplan(self):
        ctx = dict(self._context)
        ctx.update({"search_default_parent_id": self.id})
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_activity_action_from_careplan"
        )
        return dict(action, context=ctx)

    def unlink(self):
        for plan in self.with_context(active_test=False):
            if plan.child_ids:
                raise UserError(
                    _(
                        "You cannot delete a careplan containing sub care plan."
                        " You can either archive it or first delete "
                        "all of its."
                    )
                )
        return super().unlink()
