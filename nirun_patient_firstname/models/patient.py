#  Copyright (c) 2021 NSTDA

from odoo import _, api, models


class Patient(models.Model):
    _inherit = "ni.patient"

    @api.model
    def default_get(self, fields_list):
        """Invert name when getting default values."""
        result = super().default_get(fields_list)

        partner_model = self.env["res.partner"]
        inverted = partner_model._get_inverse_name(
            partner_model._get_whitespace_cleaned_name(result.get("name", "")),
            result.get("is_company", False),
        )

        for field in list(inverted.keys()):
            if field in fields_list:
                result[field] = inverted.get(field)

        return result

    @api.onchange("firstname", "lastname")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for rec in self:
            rec.name = rec.partner_id._get_computed_name(rec.lastname, rec.firstname)

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if ("name" not in default) and ("partner_id" not in default):
            default["name"] = _("%s (copy)") % self.name

        if (
            ("firstname" not in default)
            and ("lastname" not in default)
            and ("name" in default)
        ):
            default.update(
                self.env["res.partner"]._get_inverse_name(default["name"], False)
            )
        return super().copy(default)
