#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReferenceRange(models.Model):
    _name = "ni.observation.reference.range"
    _description = "Observation Reference Range"
    _order = "type_id,gender,age_low,age_high,low,high"

    _parent_store = True
    parent_id = fields.Many2one(
        "ni.observation.reference.range", index=True, ondelete="set null"
    )
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many("ni.observation.reference.range", "parent_id")

    type_id = fields.Many2one("ni.observation.type", index=True, required=True)
    low = fields.Float(help="Inclusive", group_operator="min")
    high = fields.Float(help="Exclusive", group_operator="max")
    gender = fields.Selection([("male", "Male"), ("female", "Female")], required=False)
    age_low = fields.Float(default=0, help="Inclusive", group_operator="min")
    age_high = fields.Float(default=200, help="Exclusive", group_operator="max")
    interpretation_id = fields.Many2one("ni.observation.interpretation", required=True)
    display_class = fields.Selection(related="interpretation_id.display_class")
    active = fields.Boolean(default="True")

    def name_get(self):
        return [
            (ref.id, "%s [%d-%d]" % (ref.type_id.name, ref.low, ref.high))
            for ref in self
        ]

    @api.constrains("low", "high")
    def _validate_low_high(self):
        for rec in self:
            if rec.low > rec.high:
                raise ValidationError(_("low value must not be more than high value"))

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
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
