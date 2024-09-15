#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class ConditionCode(models.Model):
    _name = "ni.condition.code"
    _description = "Condition / Problem"
    _inherit = ["ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("ni.condition.code", index=True, ondelete="cascade")
    parent_path = fields.Char(index=True, unaccent=False)

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
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

    def _get_name(self):
        coding = self
        name = coding.name
        if (
            self._context.get("show_parent")
            and "parent_id" in self._fields
            and coding._fields["parent_id"]
        ):
            names = []
            current = coding
            while current:
                names.append(current.name)
                current = current.parent_id
            name = self._display_name_separator.join(reversed(names))
        if self._context.get("show_abbr") and self.abbr:
            name = "{} ({})".format(name, coding.abbr)
        if self._context.get("show_code") and self.code:
            name = "{}  {}".format(coding.code, name)
        if self._context.get("only_abbr") and self.abbr:
            name = coding.abbr
        return name
