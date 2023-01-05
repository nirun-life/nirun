#  Copyright (c) 2023. NSTDA

from odoo import api, fields, models


class Document(models.Model):
    _name = "ni.document"
    _description = "Document Reference"
    _inherit = ["ni.patient.res"]
    _inherits = {"ir.attachment": "attachment_id"}

    type_id = fields.Many2one("ni.document.type", required=True)
    category_id = fields.Many2one("ni.document.category")
    attachment_id = fields.Many2one(
        "ir.attachment", required=True, auto_join=True, ondelete="cascade"
    )
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if "res_model" not in vals:
            if "encounter_id" in vals:
                vals.update(
                    {
                        "res_id": vals["encounter_id"],
                        "res_model": "ni.encounter",
                    }
                )
            else:
                vals.update(
                    {
                        "res_id": vals["patient_id"],
                        "res_model": "ni.patient",
                    }
                )
        return super(Document, self).create(vals)

    @api.onchange("type_id")
    def _onchange_type_id(self):
        for rec in self:
            rec.category_id = rec.type_id.category_id

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            if rec.type_id and rec.type_id.category_id != rec.category_id:
                rec.type_id = False
