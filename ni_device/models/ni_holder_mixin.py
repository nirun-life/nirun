from odoo import api, fields, models


class HolderMixin(models.AbstractModel):
    _name = "ni.holder.mixin"
    _description = "Mixin for common holder fields"

    holder_partner_id = fields.Many2one("res.partner", string="Holder")
    holder_employee_id = fields.Many2one("hr.employee", string="Holder (Employee)")
    holder_name = fields.Char("Holder Name", compute="_compute_holder_name")

    @api.depends("holder_employee_id", "holder_partner_id")
    def _compute_holder_name(self):
        for rec in self:
            rec.holder_name = (
                rec.holder_employee_id.name or rec.holder_partner_id.name or ""
            )

    @api.onchange("holder_employee_id")
    def _onchange_holder_employee(self):
        for rec in self:
            if rec.holder_employee_id:
                # autofill partner
                partner = (
                    rec.holder_employee_id.user_id.partner_id
                    or rec.holder_employee_id.address_home_id
                )
                rec.holder_partner_id = partner
