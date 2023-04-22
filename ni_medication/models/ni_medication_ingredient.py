#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models

STRENGTH_FIELDS = (
    "strength_numerator",
    "strength_numerator_unit",
    "strength_denominator",
    "strength_denominator_unit",
)


class MedicationIngredient(models.Model):
    _name = "ni.medication.ingredient"
    _description = "Medication Ingredient"

    medication_id = fields.Many2one("ni.medication", index=True, ondelete="cascade")
    name = fields.Char(required=True)
    is_active = fields.Boolean("Active Ingredient", default=True)

    strength = fields.Char(compute="_compute_strength")
    strength_numerator = fields.Float(required=False)
    strength_numerator_unit = fields.Many2one("uom.uom", required=False)
    strength_denominator = fields.Float(required=False)
    strength_denominator_unit = fields.Many2one("uom.uom", required=False)

    def name_get(self):
        return [(rec.id, "{} {}".format(rec.name, rec.strength)) for rec in self]

    @api.depends(
        "strength_numerator",
        "strength_numerator_unit",
        "strength_denominator",
        "strength_denominator_unit",
    )
    def _compute_strength(self):
        for rec in self:
            res = []
            if rec.strength_numerator and rec.strength_numerator_unit:
                res.append(
                    "{} {}".format(
                        rec.strength_numerator, rec.strength_numerator_unit.name
                    )
                )
            if rec.strength_denominator and rec.strength_denominator_unit:
                res.append(
                    "{} {}".format(
                        rec.strength_denominator, rec.strength_denominator_unit.name
                    )
                )
            rec.strength = " / ".join(res)
