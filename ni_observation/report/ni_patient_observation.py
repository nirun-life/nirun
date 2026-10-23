#  Copyright (c) 2022 Piruin P.

from odoo import models, tools
from odoo.tools import SQL


class EncounterObservationLatest(models.Model):
    _name = "ni.patient.observation"
    _description = "Patient Latest Observation"
    _auto = False
    _inherit = ["ni.observation.report"]

    def init(self):
        # NOT EXISTS instead of DISTINCT ON: PostgreSQL cannot push the ORM's
        # filter on id or survey_response_id into a DISTINCT ON subquery, so
        # each read rebuilt the view from the whole table.
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            SQL(
                """CREATE OR REPLACE VIEW %s AS (
                SELECT o.*
                FROM ni_observation o
                WHERE o.value IS NOT NULL
                  AND o.type_id IS NOT NULL
                  AND o.occurrence IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1
                    FROM ni_observation n
                    WHERE n.patient_id = o.patient_id
                      AND n.type_id = o.type_id
                      AND n.value IS NOT NULL
                      AND (n.occurrence > o.occurrence
                           OR (n.occurrence = o.occurrence AND n.id > o.id))
                  )
            )""",
                SQL.identifier(self._table),
            )
        )
