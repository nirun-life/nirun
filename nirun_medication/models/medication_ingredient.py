#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class MedicationIngredient(models.Model):
    _name = "ni.medication.ingredient"
    _description = "Medication Ingredient"

    medication_id = fields.Many2one("ni.medication", index=True)
    name = fields.Char(required=True)
    is_active = fields.Boolean("Active Ingredient", default=True)

    strength = fields.Char(compute="_compute_strength")
    strength_numerator = fields.Float(required=False)
    strength_numerator_unit = fields.Many2one("ni.quantity.unit", required=False)
    strength_denominator = fields.Float(required=False)
    strength_denominator_unit = fields.Many2one("ni.quantity.unit", required=False)

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
            if rec.strength_numerator:
                res.append(
                    "{} {}".format(
                        rec.strength_numerator, rec.strength_numerator_unit.name
                    )
                )
            if rec.strength_denominator:
                res.append(
                    "{} {}".format(
                        rec.strength_denominator, rec.strength_denominator_unit.name
                    )
                )
            rec.strength = " / ".join(res)
