#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class CareEpisode(models.Model):
    _name = "ni.care.episode"
    _description = "Episode of Care"
    _inherit = ["period.mixin", "ir.sequence.mixin"]
    _check_company_auto = True

    name = fields.Char(
        "Identifier",
        index=True,
        copy=False,
        readonly=True,
        default=lambda self: self._sequence_default,
    )

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    encounter_id = fields.Many2one(
        "ni.encounter",
        "Encounter",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )
    patient_id = fields.Many2one(
        string="Patient",
        related="encounter_id.patient_id",
        required=True,
        ondelete="cascade",
    )
    care_manager = fields.Many2one("hr.employee", "Care Manager", required=True)
