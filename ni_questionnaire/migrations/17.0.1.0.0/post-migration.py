#  Copyright (c) 2026 NSTDA
"""Recompute each encounter's latest questionnaire response.

Up to 16.0, ``ni.encounter._compute_response`` read the latest response from a SQL
view before the ORM had flushed the response to the database, and did not depend on
the response state. So the stored ``response_latest_id``, ``response_latest_grade_id``
and ``response_latest_date`` of existing encounters are empty or stale, which hides
the latest grade and the "Print Questionnaire" button. 17.0 computes them from the
responses; recompute them once for the encounters that have responses.
"""

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {"active_test": False})
    encounters = env["ni.encounter"].search([("response_ids", "!=", False)])
    for name in (
        "response_latest_id",
        "response_latest_grade_id",
        "response_latest_date",
    ):
        env.add_to_compute(encounters._fields[name], encounters)
    env.flush_all()
    _logger.info("Recomputed the latest response of %s encounters", len(encounters))
