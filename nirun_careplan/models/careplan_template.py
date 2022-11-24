#  Copyright (c) 2022 Piruin P.

from odoo import api, fields, models


class CareplanTemplateActivity(models.Model):
    _name = "ni.careplan.template.activity"
    _description = "Careplan Template Activity"
    _inherit = ["ni.careplan.activity.base"]

    careplan_id = fields.Many2one(
        "ni.careplan.template", copy=False, ondelete="cascade"
    )
    company_id = fields.Many2one(related="careplan_id.company_id", store=True)
    timing_tmpl_id = fields.Many2one("ni.timing.template")


class CareplanTemplateGoal(models.Model):
    _name = "ni.careplan.template.goal"
    _description = "Careplan Template Goal"
    _inherit = ["ni.goal"]

    careplan_id = fields.Many2one(
        "ni.careplan.template", copy=False, ondelete="cascade"
    )
    patient_id = fields.Many2one(
        required=False, store=False, check_company=False, copy=False
    )
    company_id = fields.Many2one(related="careplan_id.company_id", store=True)
    state = fields.Selection(default="proposed", compute=False)
    _sql_constraints = [
        (
            "code__uniq",
            "unique (careplan_id, code_id)",
            "Goal must be unqiue!",
        ),
    ]

    def init(self):
        """To prevent index creation cause by inherit ni.patient.res"""

    def copy_data(self, default=None):
        # Put this snippet at ni.goal not work [13.0]. May try later.
        if default is None:
            default = {}
        if "state" not in default:
            default["state"] = "proposed"
        return super().copy_data(default)


class CareplanTemplate(models.Model):
    _name = "ni.careplan.template"
    _description = "Careplan Template"
    _inherit = ["ni.careplan"]
    _check_company_auto = False
    _rec_name = "name"

    company_id = fields.Many2one(
        "res.company",
        required=False,
        related=False,
        readonly=False,
        copy=False,
        store=True,
        tracking=True,
        default=False,
    )
    patient_id = fields.Many2one(
        required=False, store=False, check_company=False, copy=False
    )
    encounter_id = fields.Many2one(
        required=False, store=False, check_company=False, copy=False
    )
    manager_id = fields.Many2one(required=False, store=False)
    contributor_ids = fields.Many2many(
        "hr.employee",
        "ni_careplan_template_contributor",
        "careplan_id",
        "contributor_id",
        check_company=False,
        copy=False,
    )

    name = fields.Char("Careplan", required=True)
    description = fields.Text(copy=True, help="Summary of nature of plan")
    sequence = fields.Integer(
        "Sequence", help="Determine the display order", index=True, default=100
    )
    period_start = fields.Date(default=False, copy=False)
    period_end = fields.Date(copy=False)

    category_ids = fields.Many2many(
        "ni.careplan.category",
        "ni_careplan_template_category_rel",
    )
    condition_ids = fields.Many2many(
        "ni.condition",
        "ni_careplan_template_condition_rel",
        readonly=True,
        store=False,
        copy=False,
    )
    condition_code_ids = fields.Many2many(
        "ni.condition.code", readonly=False, store=True, copy=False, compute=False
    )
    activity_ids = fields.One2many(
        "ni.careplan.template.activity",
        "careplan_id",
        readonly=False,
        states={},
    )
    goal_ids = fields.One2many(
        "ni.careplan.template.goal",
        "careplan_id",
        readonly=False,
        states={},
    )

    def init(self):
        """To prevent index creation cause by inherit ni.patient.res"""

    def name_get(self):
        res = []
        for plan in self:
            res.append((plan.id, plan.name))
        return res

    def copy(self, default=None):
        default = default or {}
        if "name" not in default:
            default["name"] = "%s (copy)" % (self.name)
        return super(CareplanTemplate, self).copy(default)

    @api.depends("activity_ids")
    def _compute_activities_count(self):
        for plan in self:
            plan.activity_count = len(plan.activity_ids)

    @api.depends("goal_ids")
    def _compute_goal_count(self):
        for plan in self:
            plan.goal_count = len(plan.goal_ids)
