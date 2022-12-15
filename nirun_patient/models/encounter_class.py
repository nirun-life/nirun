#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models


class EncounterClassification(models.Model):
    _name = "ni.encounter.cls"
    _description = "Encounter Classification"
    _inherit = ["coding.base"]
    _parent_store = True

    parent_id = fields.Many2one("ni.encounter.cls", string="Parent Class", index=True)
    parent_path = fields.Char(index=True, readonly=True)
    hospitalization = fields.Boolean(help="Is hospitalization classification?")
    company_id = fields.Many2one("res.company", required=False)

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
