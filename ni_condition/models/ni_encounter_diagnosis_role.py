#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DiagnosisRole(models.Model):
    _name = "ni.encounter.diagnosis.role"
    _description = "Diagnosis Role"
    _inherit = ["ni.coding"]
    _parent_store = True

    limit = fields.Integer(default=-1)
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
    parent_id = fields.Many2one(
        "ni.encounter.diagnosis.role", index=True, ondelete="cascade"
    )
    parent_path = fields.Char(index=True)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(_("Error! You cannot create recursive data."))
