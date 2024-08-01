#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResumeLine(models.Model):
    _inherit = "hr.resume.line"

    code_id = fields.Many2one("hr.resume.line.code", required=False, index=True)
    code_require_identifier = fields.Boolean(related="code_id.require_identifier")
    line_type_id = fields.Many2one("hr.resume.line.type", string="Type", index=True)
    identifier = fields.Char("Credential ID")
    issuer_id = fields.Many2one("res.partner", domain="[('is_company', '=', True)]")

    def name_get(self):
        return [(line.id, line._get_name()) for line in self]

    def _get_name(self):
        line = self
        name = line.name
        if self._context.get("show_identifier") and self.identifier:
            name = "{} • {}".format(name, line.identifier)
        if self._context.get("show_period"):
            period = [line.date_start, line.date_end or _("Current")]
            name = "{} {}".format(name, " - ".join(period))
        return name

    @api.onchange("code_id")
    def _onchange_code_id(self):
        if self.code_id:
            self.name = self.code_id.name
            if self.code_id.issuer_id:
                self.issuer_id = self.code_id.issuer_id
            if self.code_id.type_id:
                self.line_type_id = self.code_id.type_id

    @api.constrains("date_start", "date_end")
    def _check_date(self):
        for rec in self:
            if rec.date_end and rec.date_start > rec.date_end:
                # Not sure why origin's _sql_constraint not work for this case
                raise ValidationError(
                    _("The start date must be anterior to the end date.")
                )
            if rec.date_start > fields.Date.today():
                raise ValidationError(_("The start Date must not be in the future."))
