#  Copyright (c) 2021-2023 NSTDA
import ast

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Patient(models.Model):
    _inherit = "ni.patient"

    allergy_ids = fields.One2many(
        "ni.allergy", "patient_id", "Allergy List", check_company=True
    )
    allergy_code_ids = fields.Many2many(
        "ni.allergy.code",
        string="Allergy Substance List",
        compute="_compute_allergy",
        inverse="_inverse_allergy",
    )
    allergy = fields.Selection(
        [
            ("identified", "Identified"),
            ("unknown", "No Known Allergy"),
            ("not-ask", "Not Asked"),
        ],
        "Allergy / Intolerance",
    )
    allergy_count = fields.Integer(compute="_compute_allergy")

    def _inverse_allergy(self):
        # This inverse function is good for simple version if require detail in allergy
        # 'allergy_code' should always set as READONLY
        # NOTE this also not work as expected on encounter form
        params = self._context.get("params", {})
        for rec in self:
            cmd = []
            rmv = [
                fields.Command.delete(allergy.id)
                for allergy in rec.allergy_ids
                if allergy.code_id not in rec.allergy_code_ids
            ]
            for code in rec.allergy_code_ids:
                if not rec.allergy_ids.filtered_domain([("code_id", "=", code.id)]):
                    val = {"code_id": code.id}
                    if params.get("model") == "ni.encounter":
                        val["encounter_id"] = params.get("id")
                    cmd += [fields.Command.create(val)]
            if cmd or rmv:
                cmd = rmv + cmd
                rec.allergy_ids = cmd

    @api.depends("allergy_ids")
    def _compute_allergy(self):
        for rec in self:
            rec.allergy_count = len(rec.allergy_ids)
            rec.allergy_code_ids = rec.allergy_ids.mapped("code_id")

    def action_view_allergy(self, ctx=None):
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            ._for_xml_id("ni_allergy.ni_allergy_action")
        )
        action["display_name"] = _("%(name)s's Allergy", name=self.name)
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        context.update(
            {
                "create": self.active,
                "active_test": self.active,
                "default_patient_id": self.id,
            }
        )
        if ctx:
            context.update(ctx)
        action["context"] = context
        action["domain"] = [("patient_id", "=", self.id)]
        return action

    def action_add_allergy(self, ctx=None):
        action = self.action_view_allergy(ctx)
        action["view_mode"] = "form"
        action["views"] = [(False, "form")]
        action["target"] = "new"
        return action

    @api.constrains("allergy_ids", "allergy")
    def _check_allergy(self):
        for rec in self:
            if rec.allergy != "identified" and rec.allergy_ids:
                rec.allergy_ids = [fields.Command.clear()]
            if rec.allergy == "identified" and not rec.allergy_ids:
                raise UserError(_("Must identify at least one allergy record"))
