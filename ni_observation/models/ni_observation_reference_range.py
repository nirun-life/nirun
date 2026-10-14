#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ReferenceRange(models.Model):
    _name = "ni.observation.reference.range"
    _description = "Observation Reference Range"
    _order = "type_id,gender,age_low,age_high,low,high"

    _parent_store = True
    parent_id = fields.Many2one(
        "ni.observation.reference.range", index=True, ondelete="set null"
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("ni.observation.reference.range", "parent_id")

    type_id = fields.Many2one("ni.observation.type", index=True, required=True)
    low = fields.Float(help="Inclusive", aggregator="min")
    high = fields.Float(help="Exclusive", aggregator="max")
    gender = fields.Selection([("male", "Male"), ("female", "Female")], required=False)
    age_low = fields.Float(default=0, help="Inclusive", aggregator="min")
    age_high = fields.Float(default=200, help="Exclusive", aggregator="max")
    interpretation_id = fields.Many2one("ni.observation.interpretation", required=True)
    display_class = fields.Selection(related="interpretation_id.display_class")
    active = fields.Boolean(default="True")
    is_problem = fields.Boolean(related="interpretation_id.is_problem")

    @api.depends("type_id.name", "low", "high")
    def _compute_display_name(self):
        for ref in self:
            ref.display_name = f"{ref.type_id.name} [{int(ref.low)}-{int(ref.high)}]"

    @api.constrains("low", "high")
    def _validate_low_high(self):
        for rec in self:
            if rec.low > rec.high:
                raise ValidationError(
                    self.env._("low value must not be more than high value")
                )

    @api.model
    def range_for(self, type_id, age=0, gender=None):
        return self.search(
            [
                ("type_id", "=", type_id),
                "|",
                ("gender", "=", gender),
                ("gender", "=", False),
                ("age_low", "<=", age),
                ("age_high", ">=", age),
            ]
        )

    def interpret(self, value):
        for rec in self:
            if rec.low <= value <= rec.high:
                return rec

            for c in rec.child_ids:
                ref = c.interpret(value)
                if ref:
                    return ref
        return None

    @api.constrains("parent_id", "age_low", "age_high")
    def _check_age_range(self):
        for rec in self:
            if not rec.parent_id:
                continue
            if rec.age_low != rec.parent_id.age_low:
                rec.age_low = rec.parent_id.age_low
            if rec.age_high != rec.parent_id.age_high:
                rec.age_high = rec.parent_id.age_high

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(
                self.env._("Error! You cannot create recursive data.")
            )
