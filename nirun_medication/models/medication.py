#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


class Medication(models.Model):
    _name = "ni.medication"
    _description = "Medication"

    name = fields.Char(index=True)
    active = fields.Boolean(default=True)
    manufacturer_name = fields.Char()
    manufacturer_id = fields.Many2one("res.partner", domain=[("is_company", "=", True)])
    form = fields.Many2one("ni.medication.form")
    ingredient = fields.Char("Ingredient", compute="_compute_ingredient")
    ingredient_ids = fields.One2many("ni.medication.ingredient", "medication_id")
    amount = fields.Char(compute="_compute_amount")
    amount_numerator = fields.Float()
    amount_numerator_unit = fields.Many2one("ni.quantity.unit")
    amount_denominator = fields.Float(default=1.0, require=True)
    amount_denominator_unit = fields.Many2one("ni.quantity.unit", required=True)

    def name_get(self):
        return [
            (
                rec.id,
                "%s (%s) (%s) %s"
                % (rec.name, rec.manufacturer_name, rec.ingredient, rec.form.name),
            )
            for rec in self
        ]

    @api.depends("ingredient_ids")
    def _compute_ingredient(self):
        for rec in self:
            ingredient = [ing.display_name for ing in rec.ingredient_ids]
            rec.ingredient = " + ".join(ingredient)

    @api.depends(
        "amount_numerator",
        "amount_numerator_unit",
        "amount_denominator",
        "amount_denominator_unit",
    )
    def _compute_amount(self):
        for rec in self:
            res = []
            if rec.amount_numerator:
                res.append(
                    "{} {}".format(rec.amount_numerator, rec.amount_numerator_unit.name)
                )
            if rec.amount_denominator != 1:
                res.append(
                    "{} {}".format(
                        rec.amount_denominator, rec.amount_denominator_unit.name
                    )
                )
            else:
                res.append(rec.amount_denominator_unit.name)
            rec.amount = " ".join(res)
