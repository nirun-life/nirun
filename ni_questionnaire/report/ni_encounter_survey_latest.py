#  Copyright (c) 2022 Piruin P.

from odoo import models


class EncounterSurveyLatest(models.Model):
    _name = "ni.encounter.survey_latest"
    _description = "Encounter's latest survey result"
    _inherit = ["ni.patient.survey_latest"]
    _auto = False

    def init(self):
        self._create_latest_view("encounter_id")
