#  Copyright (c) 2021 NSTDA
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Medication(models.Model):
    _inherit = "ni.medication"

    tpu_code = fields.Char(limit=7, index=True)
    fsn = fields.Char(compute="_compute_fsn", store=True, index=True)
    active_ingredient = fields.Char()
    strength = fields.Char()

    def name_get(self):
        return [(rec.id, rec.fsn) for rec in self]

    @api.model
    def create(self, vals):
        vals = self._compute_ingredient_val(vals)
        return super().create(vals)

    def write(self, vals):
        vals = self._compute_ingredient_val(vals)
        return super().write(vals)

    @api.model
    def _compute_ingredient_val(self, vals):
        try:
            if vals.get("active_ingredient") and "strength" in vals:
                ingredients = vals.get("active_ingredient").split("+")
                strengths = vals.get("strength").split("+")
                res = [
                    "{} {}".format(ingredients[i].strip(), strengths[i].strip())
                    for i in range(len(ingredients))
                ]
                vals["ingredient"] = " + ".join(res)
        finally:
            return vals

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += ["|", ("fsn", operator, name), ("tpu_code", operator, name)]
        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(ids).with_user(name_get_uid))

    @api.depends("name", "manufacturer_name", "ingredient", "form", "amount")
    def _compute_fsn(self):
        for rec in self:
            rec.fsn = "".join(
                filter(
                    None,
                    (
                        rec.name,
                        rec.name_manufacturer,
                        rec.name_ingredient,
                        rec.name_form,
                        rec.name_amount,
                    ),
                )
            )

    @property
    def name_manufacturer(self):
        return " (%s)" % self.manufacturer_name if self.manufacturer_name else ""

    @property
    def name_ingredient(self):
        return " (%s)" % self.ingredient if self.ingredient else ""

    @property
    def name_form(self):
        return " %s" % self.form.name if self.form else ""

    @property
    def name_amount(self):
        return ", %s" % self.amount if self.amount else ""
