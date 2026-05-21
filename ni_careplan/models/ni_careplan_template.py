#  Copyright (c) 2025 NSTDA
from odoo import api, fields, models


class CareplanTemplate(models.Model):
    _name = "ni.careplan.template"
    _description = "Careplan Template"
    _inherit = "ni.coding"

    company_id = fields.Many2one("res.company", required=False, index=True)
    category_id = fields.Many2one(
        "ni.careplan.category",
        required=False,
        index=True,
    )
    condition_code_ids = fields.Many2many(
        "ni.condition.code",
        "ni_careplan_template_condition_code",
        "template_id",
        "code_id",
    )

    goal_category_id = fields.Many2one(related="category_id.goal_category_id")
    goal_code_ids = fields.Many2many(
        "ni.goal.code", "ni_careplan_template_goal_code", "template_id", "code_id"
    )
    observation_type_ids = fields.Many2many(
        "ni.observation.type",
        "ni_careplan_template_observation_type_rel",
        "template_id",
        "type_id",
        string="Observation Types",
    )
    service_category_id = fields.Many2one(related="category_id.service_category_id")
    service_request_ids = fields.One2many(
        "ni.careplan.template.service.request", "template_id"
    )
    medication_request_ids = fields.One2many(
        "ni.careplan.template.medication.request", "template_id"
    )


class ServiceRequestTemplate(models.Model):
    _name = "ni.careplan.template.service.request"

    company_id = fields.Many2one(related="template_id.company_id", copy=False)
    template_id = fields.Many2one("ni.careplan.template", copy=False)
    name = fields.Char("Service Name", required=True)
    category_id = fields.Many2one(
        "ni.service.category",
        domain=lambda self: [
            ("id", "!=", self.env.ref("ni_service.categ_routine").id),
        ],
    )
    timing_tmpl_id = fields.Many2one("ni.timing.template")
    service_ids = fields.Many2many(
        "ni.service",
        "ni_careplan_template_service_request_code",
        "request_id",
        "code_id",
        check_company=True,
    )

    def _default_service_domain(self):
        return [("category_id", "!=", self.env.ref("ni_service.categ_routine").id)]

    @api.onchange("category_id")
    def _onchange_category_id(self):
        if self.category_id:
            domain = [("category_id", "=", self.category_id.id)]
        else:
            domain = self._default_service_domain()
        return {"domain": {"service_ids": domain}}

    @api.onchange("service_ids")
    def _onchange_service_ids(self):
        for rec in self:
            if rec.service_ids:
                name = ", ".join(rec.service_ids.mapped("name"))
                rec.name = name[:128] if len(name) > 128 else name

    def copy_data(self, default=None):
        # if not "timing_id" in default and not self.timing_id:
        # default["timing_id"] = self.timing_tmpl_id.id
        return super().copy_data(default)


class MedicationRequestTemplate(models.Model):
    _name = "ni.careplan.template.medication.request"
    _description = "Careplan Template Medication Request"
    _inherit = "ni.medication.abstract"

    company_id = fields.Many2one(
        related="template_id.company_id", copy=False, store=True
    )
    template_id = fields.Many2one(
        "ni.careplan.template", required=True, copy=False, ondelete="cascade"
    )
    quantity = fields.Float("Qty", default=1.0, required=True)
    note = fields.Char()

    def copy_data(self, default=None):
        default = dict(default or {})
        copied_vals = super().copy_data(default)[0]
        if self.timing_id:
            copied_vals.update(
                {
                    "timing_frequency": self.timing_frequency,
                    "timing_frequency_max": self.timing_frequency_max,
                    "timing_duration": self.timing_duration,
                    "timing_duration_max": self.timing_duration_max,
                    "timing_duration_unit": self.timing_duration_unit,
                    "timing_period": self.timing_period,
                    "timing_period_max": self.timing_period_max,
                    "timing_period_unit": self.timing_period_unit,
                    "timing_offset": self.timing_offset,
                    "timing_tmpl_id": self.timing_tmpl_id.id
                    if self.timing_tmpl_id
                    else False,
                    "timing_when": [(6, 0, self.timing_when.ids)]
                    if self.timing_when
                    else [(5, 0, 0)],
                    "timing_dow": [(6, 0, self.timing_dow.ids)]
                    if self.timing_dow
                    else [(5, 0, 0)],
                    "timing_tod": [(6, 0, self.timing_tod.ids)]
                    if self.timing_tod
                    else [(5, 0, 0)],
                }
            )
        return [copied_vals]
