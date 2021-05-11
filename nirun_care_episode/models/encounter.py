#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    episode_ids = fields.Many2many(
        "ni.care.episode",
        "ni_care_episode_encounter" "encounter_id",
        "episode_id" "Episodes of care",
        states={"cancelled": [("readonly", True)], "finished": [("readonly", True)]},
        help="Episode(s) of care that this encounter should be recorded against",
    )
