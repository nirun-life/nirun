#  Copyright (c) 2026 NSTDA
"""Repair the start dates written by the old ``period_start_date`` default.

Up to 16.0.0.1.0, ``period_start_date`` defaulted to today. On create a default
counts as a given value, so the compute never ran: every record created from
code (import, RPC, bulk wizards) stored its creation day instead of the date of
its ``period_start``.

This runs as an ``end-`` script because ``ni_period`` has no dependencies: at
``post-`` time none of the models that use the mixin are loaded yet.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

MIXIN = "ni.period.mixin"


def _defines_own_start_date(model):
    """True when the model (or an extension of it) declares its own
    ``period_start_date``; ``ni.condition`` did, with ``default=None``, so the
    bug never reached it."""
    for cls in type(model).mro()[1:]:
        if "period_start_date" in vars(cls) and getattr(cls, "_name", None) != MIXIN:
            return True
    return False


def _models_to_fix(env):
    for model_name in sorted(env.registry.descendants([MIXIN], "_inherit")):
        model = env[model_name]
        if model._abstract or not model._auto or _defines_own_start_date(model):
            continue
        yield model


def fix_period_start_date(env):
    for model in _models_to_fix(env):
        # Only datetime-mode rows: in date mode the inverse leaves period_start
        # alone when the user edits the date, so a mismatch can be intended.
        # The old default used the creating user's timezone, hence +/- 1 day.
        env.cr.execute(
            f"""
            UPDATE "{model._table}"
            SET period_start_date = period_start::date
            WHERE period_mode = 'datetime'
              AND period_start IS NOT NULL
              AND period_start_date <> period_start::date
              AND period_start_date BETWEEN create_date::date - 1
                                        AND create_date::date + 1
            """
        )
        if env.cr.rowcount:
            _logger.info(
                "ni_period: fixed period_start_date on %s %s rows",
                env.cr.rowcount,
                model._name,
            )
            model.invalidate_model(["period_start_date"])


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    fix_period_start_date(env)
