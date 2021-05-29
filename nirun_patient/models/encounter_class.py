#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models


class EncounterClassification(models.Model):
    _name = "ni.encounter.cls"
    _description = "Encounter Classification"
    _inherit = ["coding.base"]
    _parent_store = True

    parent_id = fields.Many2one("ni.encounter.cls", string="Parent Class", index=True)
    parent_path = fields.Char(index=True, readonly=True)

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

    def name_get(self):
        res = []
        for enc_cls in self:
            names = []
            current = enc_cls
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((enc_cls.id, ", ".join(reversed(names))))
        return res
