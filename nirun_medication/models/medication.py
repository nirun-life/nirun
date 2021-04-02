#  Copyright (c) 2021 Piruin P.
from odoo import api, fields, models


class Medication(models.Model):
    _name = "ni.medication"
    _description = "Medication"

    name = fields.Char(index=True)
    active = fields.Boolean(default=True)
    manufacturer_name = fields.Char(index=True)
    manufacturer_id = fields.Many2one("res.partner", domain=[("is_company", "=", True)])
    form = fields.Many2one("ni.medication.form", index=True)
    ingredient = fields.Char(
        "Ingredient", compute="_compute_ingredient", store=True, index=True
    )
    ingredient_ids = fields.One2many(
        "ni.medication.ingredient", "medication_id", "Ingredient List"
    )
    amount = fields.Char(compute="_compute_amount", store=True, index=True)
    amount_numerator = fields.Float()
    amount_numerator_unit = fields.Many2one("ni.quantity.unit")
    amount_denominator = fields.Float(default=1.0)
    amount_denominator_unit = fields.Many2one("ni.quantity.unit")

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += [
                "|",
                "|",
                ("name", operator, name),
                ("manufacturer_name", operator, name),
                ("ingredient", operator, name),
            ]
        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(ids).with_user(name_get_uid))

    @api.depends("ingredient_ids")
    def _compute_ingredient(self):
        for rec in self:
            if rec.ingredient_ids:
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
            elif not rec.amount_numerator:
                res.append("1 {}".format(rec.amount_denominator_unit.name))
            else:
                res.append(rec.amount_denominator_unit.name)
            rec.amount = " ".join(res)

    @api.onchange("manufacturer_id")
    def _onchange_manufacturer_id(self):
        for rec in self:
            if rec.manufacturer_id:
                rec.manufacturer_name = rec.manufacturer_id.name
