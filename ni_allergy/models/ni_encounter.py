#  Copyright (c) 2022-2023 NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    allergy_code_ids = fields.Many2many(
        "ni.allergy.code",
        string="Allergy / Intolerance",
        compute="_compute_allergy",
        inverse="_inverse_allergy",
    )
    allergy_code_count = fields.Integer(compute="_compute_allergy")
    # NOTE Can't use code_ids pattern on patient without duplicate the codes because of
    # behavior of delegate inheritance, so Implement only apply on Encounter

    @api.onchange("allergy_code_ids")
    def _onchange_allergy_code_ids(self):
        for rec in self:
            rec.allergy_code_count = len(rec.allergy_code_ids)

    @api.depends("allergy_ids")
    def _compute_allergy(self):
        for rec in self:
            rec.allergy_code_ids = rec.allergy_ids.mapped("code_id")
            rec.allergy_code_count = len(rec.allergy_code_ids)

    def _inverse_allergy(self):
        for rec in self:
            # remove all allergy that have been removed
            cmd = [
                (2, c.id, 0)
                for c in rec.allergy_ids.filtered_domain(
                    [("code_id", "not in", rec.allergy_code_ids.ids)]
                )
            ]
            # Then add new allergy
            cmd = cmd + [
                (
                    0,
                    0,
                    {
                        "code_id": p.id,
                        "patient_id": rec.patient_id.id,
                        "encounter_id": rec.id,
                    },
                )
                for p in rec.allergy_code_ids
                if p not in rec.allergy_ids.mapped("code_id")
            ]
            if cmd:
                rec.write({"allergy_ids": cmd})
