#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RelatedPerson(models.Model):
    _name = "ni.patient.related.person"
    _description = "Related Person"
    _inherit = "ni.period.mixin"
    _inherits = {"res.partner": "partner_id"}
    _order = "sequence"

    @api.model
    def default_get(self, fields):
        res = super(RelatedPerson, self).default_get(fields)
        if "parent_id" in fields and "parent_id" not in res:
            if self.env.context.get("active_model") == "ni.patient":
                res["patient_id"] = self.env.context["active_id"]
        return res

    sequence = fields.Integer()
    input = fields.Selection(
        [("new", "New"), ("search", "Search")],
        default="new",
        required=True,
        store=False,
    )
    partner_id = fields.Many2one(
        "res.partner", "Related Partner", required=True, ondelete="cascade"
    )
    patient_id = fields.Many2one(
        "ni.patient", "Related Patient", required=True, ondelete="cascade"
    )
    relationship_ids = fields.Many2many("ni.patient.relationship", required=True)

    def action_copy_parent_address(self):
        self.ensure_one()
        if not self.patient_id:
            return

        address_fields = self.patient_id.partner_id._address_fields()
        if any(self.patient_id[key] for key in address_fields):

            def convert(value):
                return value.id if isinstance(value, models.BaseModel) else value

            value = {key: convert(self.parent_id[key]) for key in address_fields}
            self.update(value)

    @api.constrains("partner_id", "patient_id")
    def _check_no_recursive(self):
        for rec in self:
            if rec.partner_id == rec.patient_id.partner_id:
                raise UserError(_("Patient must not related to themselves"))
