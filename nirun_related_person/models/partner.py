#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(selection_add=[("relate", "Related Person")])

    relationship_id = fields.Many2one(
        "res.partner.relationship",
        help="Relationship of this partner to their related partner [parent_id]",
    )

    @api.onchange("parent_id")
    def onchange_parent_id(self):
        # return values in result, as this method is used by _fields_sync()
        if not self.parent_id:
            return
        result = super(Partner, self).onchange_parent_id() or {}
        partner = self._origin

        if partner.type == "relate" or self.type == "relate":
            # for other: it convenient for user to have some prepared address
            address_fields = self._address_fields()
            if any(self.parent_id[key] for key in address_fields):

                def convert(value):
                    return value.id if isinstance(value, models.BaseModel) else value

                result["value"] = {
                    key: convert(self.parent_id[key]) for key in address_fields
                }
        return result

    def action_copy_parent_address(self):
        self.ensure_one()
        if not self.parent_id:
            return
        address_fields = self._address_fields()
        if any(self.parent_id[key] for key in address_fields):

            def convert(value):
                return value.id if isinstance(value, models.BaseModel) else value

            value = {key: convert(self.parent_id[key]) for key in address_fields}
            self.update(value)
