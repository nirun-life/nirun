#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    relate_person = fields.Boolean(compute="_compute_relate_person", store=True)

    relationship_id = fields.Many2one(
        "res.partner.relationship",
        help="Relationship of this partner to their related partner [parent_id]",
        tracking=True,
    )

    @api.model
    def default_get(self, default_fields):
        """
        FIXME
        we Found that 'default_parent_id' for res.partner have a
        chance to mess up with mail.message's parent_id
        make user unable to create partner.

        So work around solution is use `default_partner_parent_id` instead
        """
        values = super().default_get(default_fields)
        if self._context.get("default_partner_parent_id"):
            values["parent_id"] = self._context.get("default_partner_parent_id")
        return values

    @api.onchange("parent_id")
    @api.depends("parent_id.patient")
    def _compute_relate_person(self):
        for rec in self:
            if rec.parent_id and rec.parent_id.patient:
                rec.relate_person = True
            else:
                rec.relate_person = False

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
