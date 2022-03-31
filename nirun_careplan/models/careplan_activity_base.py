#  Copyright (c) 2022 Piruin P.

from odoo import api, fields, models


class Activity(models.AbstractModel):
    _name = "ni.careplan.activity.base"
    _description = "Careplan Activity"
    _order = "sequence"

    sequence = fields.Integer(help="Determine the display order", index=True)
    color = fields.Integer(string="Color Index")

    careplan_id = fields.Many2one(
        "ni.careplan",
        string="Care Plan",
        required=True,
        check_company=True,
        ondelete="cascade",
        copy=False,
        default=lambda self: self.env.context.get("default_careplan_id"),
    )
    company_id = fields.Many2one(
        related="careplan_id.company_id", store=True, readonly=True, index=True
    )
    code_id = fields.Many2one(
        "ni.careplan.activity.code",
        "Activity",
        required=True,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    name = fields.Char(string="Activity", related="code_id.name")
    description = fields.Html(string="Description")
    category_id = fields.Many2one("ni.careplan.category", tracking=True)
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Important")],
        default="0",
        index=True,
        string="Priority",
    )
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("in-progress", "In-Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
        tracking=True,
        copy=False,
        group_expand="_group_expand_state",
    )
    _sql_constraints = [
        (
            "code__uniq",
            "unique (careplan_id, code_id)",
            "Activity must be unqiue!",
        ),
    ]

    @api.model
    def _group_expand_state(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            if rec.category_id and not rec.color:
                rec.color = rec.category_id.color
