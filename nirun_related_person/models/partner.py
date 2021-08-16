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
