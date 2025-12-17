from odoo import api, fields, models


class HolderMixin(models.AbstractModel):
    _name = "ni.holder.mixin"
    _description = "Mixin for common holder fields"

    holder_partner_id = fields.Many2one("res.partner", string="Holder")
    holder_employee_id = fields.Many2one("hr.employee", string="Holder (Employee)")
    holder_name = fields.Char("Holder Name", compute="_compute_holder_name")

    is_holder = fields.Boolean(
        compute="_compute_is_holder", store=False, search="_search_is_holder"
    )
    is_manager = fields.Boolean(compute="_compute_is_manager", store=False)

    @api.depends()
    def _compute_is_manager(self):
        user = self.env.user
        for rec in self:
            rec.is_manager = user.has_group("ni_patient.group_manager")

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

    @api.depends("holder_partner_id", "holder_partner_id.user_id")
    def _compute_is_holder(self):
        current_user = self.env.user
        current_partner = current_user.partner_id
        for rec in self:
            rec.is_holder = False
            if not rec.holder_partner_id:
                continue
            # ครอบคลุมทั้งกรณี partner ถูกผูกกับ user และกรณี partner ตรงกับ user's partner
            if (
                rec.holder_partner_id.user_id
                and rec.holder_partner_id.user_id == current_user
            ):
                rec.is_holder = True
            elif rec.holder_partner_id == current_partner:
                rec.is_holder = True
            else:
                rec.is_holder = False

    def _search_is_holder(self, operator, value):
        user = self.env.user
        partner_ids = [user.partner_id.id] + self.env["res.partner"].search(
            [("user_id", "=", user.id)]
        ).ids

        if value:  # is_holder = True
            return [("holder_partner_id", "in", partner_ids)]
        else:  # is_holder = False
            return [
                "|",
                ("holder_partner_id", "not in", partner_ids),
                ("holder_partner_id", "=", False),
            ]
