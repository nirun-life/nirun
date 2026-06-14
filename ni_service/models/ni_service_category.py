#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ServiceCategory(models.Model):
    _name = "ni.service.category"
    _description = "Service Category"
    _inherit = "ni.coding"

    _parent_store = True

    company_id = fields.Many2one(
        "res.company",
        required=False,
        index=True,
        default=lambda self: self.env.user.company_id,
    )
    decoration = fields.Selection(
        [
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("muted", "Muted"),
        ],
        default="muted",
        required=True,
    )

    parent_id = fields.Many2one("ni.service.category", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)
    service_ids = fields.Many2many(
        "ni.service",
        "ni_service_category_rel",
        "category_id",
        "service_id",
        string="Services",
    )
    specialty_ids = fields.Many2many(
        "hr.job", "ni_service_category_specialty", "category_id", "job_id"
    )
    fold = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group("ni_patient.group_admin"):
            allowed_company_ids = set(self.env.user.company_ids.ids)
            for vals in vals_list:
                company_id = vals.get("company_id")
                if not company_id or company_id not in allowed_company_ids:
                    raise AccessError(
                        _(
                            "Only service administrators can create or move shared service categories."
                        )
                    )
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.user.has_group("ni_patient.group_admin"):
            allowed_company_ids = set(self.env.user.company_ids.ids)
            target_company_id = vals.get("company_id")
            if target_company_id is not None:
                if (
                    not target_company_id
                    or target_company_id not in allowed_company_ids
                ):
                    raise AccessError(
                        _(
                            "Only service administrators can create or move shared service categories."
                        )
                    )
            shared = self.filtered(
                lambda rec: not rec.company_id
                or rec.company_id.id not in allowed_company_ids
            )
            if shared:
                raise AccessError(
                    _("Only service administrators can edit shared service categories.")
                )
        return super().write(vals)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
