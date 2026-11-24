#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ConditionCode(models.Model):
    _name = "ni.condition.code"
    _description = "Condition / Problem"
    _inherit = ["ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("ni.condition.code", index=True, ondelete="cascade")
    parent_path = fields.Char(index=True)

    specialty_ids = fields.Many2many(
        "hr.job",
        "ni_condition_code_specialty",
        "code_id",
        "job_id",
        help="Specialty who can use this code",
    )

    observation_code_ids = fields.Many2many(
        "ni.observation.type",
        "ni_condition_code_observation_code",
        "condition_code_id",
        "observation_code_id",
        string="Observation",
    )
    observation_code_count = fields.Integer(
        "Observation Count", compute="_compute_observation_code_count"
    )

    _sql_constraints = [
        (
            "system_name_uniq",
            "unique (system_id, parent_id, name)",
            "This name already exists!",
        ),
    ]

    @api.depends("observation_code_ids")
    def _compute_observation_code_count(self):
        for rec in self:
            rec.observation_code_count = len(rec.observation_code_ids)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(_("Error! You cannot create recursive data."))

    def _get_name(self):
        # Same as ni.coding, but the code goes first without brackets
        coding = self.with_context(show_code=False)
        name = super(ConditionCode, coding)._get_name()
        context = self.env.context
        if context.get("only_abbr") and self.abbr:
            return name
        if context.get("show_code") and self.code:
            name = f"{self.code}  {name}"
        return name
