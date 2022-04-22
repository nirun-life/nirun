#  Copyright (c) 2022 Piruin P.

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    careplan_ids = fields.One2many("ni.careplan", "encounter_id")
    careplan_count = fields.Integer(
        compute="_compute_careplan_count", store=True, compute_sudo=True
    )
    careplan_need_confirm = fields.Boolean(
        compute="_compute_careplan_count", compute_sudo=True
    )

    @api.depends("careplan_ids")
    def _compute_careplan_count(self):
        for rec in self:
            rec.write(
                {
                    "careplan_count": len(rec.careplan_ids),
                    "careplan_need_confirm": len(
                        rec.careplan_ids.filtered(lambda g: g.state == "draft")
                    ),
                }
            )

    def action_careplan_confirm(self):
        self.mapped("careplan_ids").action_confirm()
