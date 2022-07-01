#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class CareEpisode(models.Model):
    _name = "ni.care.episode"
    _description = "Episode of Care"
    _inherit = [
        "period.mixin",
        "ir.sequence.mixin",
    ]
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
    patient_id = fields.Many2one(
        string="Patient", required=True, ondelete="cascade", check_company=True
    )

    condition_ids = fields.Many2many(
        "ni.patient.condition",
        "ni_care_episode_condition" "episode_id",
        "encounter_id",
        "Conditions",
        domain=[("patient_id", "=", patient_id)],
        help="Conditions/problems/diagnoses this episode of care is for",
    )

    encounter_ids = fields.Many2many(
        "ni.encounter",
        "ni_care_episode_encounter",
        "episode_id",
        "encounter_id",
        "Encounters",
        readonly=True,
        copy=False,
    )
    care_manager = fields.Many2one("hr.employee", "Care Manager", required=True)
