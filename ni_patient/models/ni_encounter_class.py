#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class EncounterClassification(models.Model):
    _name = "ni.encounter.class"
    _description = "Encounter Classification"
    _inherit = ["ni.coding"]
    _parent_store = True

    parent_id = fields.Many2one("ni.encounter.class", string="Parent Class", index=True)
    parent_path = fields.Char(index=True, unaccent=False)
    hospitalization = fields.Boolean(help="Is hospitalization classification?")
    company_id = fields.Many2one("res.company", required=False)

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
