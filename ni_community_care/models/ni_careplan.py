#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class Careplan(models.Model):
    _name = "ni.careplan"
    _description = "แผนการให้ความช่วยเหลือ"
    _inherit = ["ni.workflow.request.mixin"]

    @api.model
    def default_get(self, fields):
        res = super(Careplan, self).default_get(fields)
        if "condition_category_id" in fields and "condition_category_id" not in res:
            categ = self.env["ni.condition.category"].search([], limit=1)
            if categ:
                res["condition_category_id"] = categ.id
                s_categ = self.env["ni.condition.category"].search(
                    [("code", "=", categ.code)], limit=1
                )
                if s_categ:
                    res["service_category_id"] = s_categ.id
        return res

    condition_category_id = fields.Many2one("ni.condition.category")
    condition_category_ids = fields.Many2many(
        "ni.condition.category",
        string="มิติ",
        compute="_compute_condition_category_ids",
    )

    condition_ids = fields.Many2many(
        "ni.condition.code", domain="[('category_id', '=?', condition_category_id)]"
    )
    condition_text = fields.Text("ประเด็นปัญหา/ความต้องการอื่นๆ")
    problem_text = fields.Text(
        "ประเด็นปัญหา/ความต้องการ", compute="_compute_problem_text"
    )
    goal_text = fields.Text("เป้าหมาย", required=True)
    service_category_id = fields.Many2one("ni.service.category")
    service_ids = fields.Many2many(
        "ni.service",
        "ni_careplan_service",
        "careplan_id",
        "service_id",
        domain="[('category_id', '=?', service_category_id)]",
    )
    service_text = fields.Text("แผนการให้ความช่วยเหลืออื่นๆ")
    action_text = fields.Text("แผนการให้ความช่วยเหลือ", compute="_compute_action_text")
    outcome = fields.Text("ผลการให้ความช่วยเหลือ")

    @api.onchange("condition_category_id")
    def _onchange_condition_category_id(self):
        for rec in self:
            rec.service_category_id = self.env["ni.service.category"].search(
                [("code", "=", rec.condition_category_id.code)], limit=1
            )
            rec.condition_ids = rec.patient_id.condition_code_ids.filtered_domain(
                [("category_id", "=", rec.condition_category_id.id)]
            )

    @api.depends("condition_category_id")
    def _compute_condition_category_ids(self):
        for rec in self:
            rec.condition_category_ids = [
                (fields.Command.set([rec.condition_category_id.id]))
            ]

    @api.depends("service_ids", "service_text")
    def _compute_action_text(self):
        for rec in self:
            txt = ", ".join(rec.service_ids.mapped("name")) if rec.service_ids else ""
            txt = " ".join([txt, rec.service_text or ""]).strip()
            rec.action_text = txt

    @api.depends("condition_ids", "condition_text")
    def _compute_problem_text(self):
        for rec in self:
            txt = (
                ", ".join(rec.condition_ids.mapped("name")) if rec.condition_ids else ""
            )
            txt = " ".join([txt, rec.condition_text or ""]).strip()
            rec.problem_text = txt
