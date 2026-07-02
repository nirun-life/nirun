#  Copyright (c) 2021-2023 NSTDA

import logging
from datetime import datetime, time

import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class EncounterClassification(models.Model):
    _name = "ni.encounter.class"
    _description = "Encounter Classification"
    _inherit = ["ni.coding"]
    _parent_store = True

    decoration = fields.Selection(
        [
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("muted", "Muted"),
        ],
        default="muted",
        required=True,
    )

    company_id = fields.Many2one("res.company", required=False)

    parent_id = fields.Many2one("ni.encounter.class", string="Parent Class", index=True)
    parent_path = fields.Char(index=True, unaccent=False)

    sequence_id = fields.Many2one(
        "ir.sequence", help="Fallback to default sequence when leave this field empty"
    )
    report_title = fields.Char(default="Summary Report")

    auto_close = fields.Boolean(default=False)
    auto_close_midnight = fields.Boolean(
        default=True,
        help="Use local midnight (encounter company's timezone, falling back to "
        "UTC) as the day boundary, instead of a fixed elapsed duration",
    )
    auto_close_offset_number = fields.Integer(default=1, readonly=False)
    auto_close_offset_type = fields.Selection(
        [
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Offset Unit",
        default="days",
    )
    # Configuration
    admission = fields.Boolean(
        default=False, help="Is this encounter class have the admission detail"
    )
    special = fields.Boolean(
        default=False, help="Diet preferences, Special courtesies and arrangement"
    )
    history = fields.Boolean(help="Show/Hide History")
    chief_complaint = fields.Boolean(default=True, help="Show/Hide Chief Complaint")
    history_of_present_illness = fields.Boolean(
        default=True, help="Show/Hide History of Present Illness"
    )
    review_of_systems = fields.Boolean(default=True, help="Show/Hide Review of Systems")
    physical_exam = fields.Boolean(default=True, help="Show/Hide Physical Examination")
    vital_signs = fields.Boolean(default=True, help="Show/Hide Vital Signs")
    laboratory = fields.Boolean(default=True, help="Show/Hide Laboratory")
    problem_list = fields.Boolean(default=True, help="Show/Hide Problem List")
    order = fields.Boolean(default=True, help="Show/Hide Order")
    medication = fields.Boolean(default=True, help="Show/Hide Medication")
    procedure = fields.Boolean(default=True, help="Show/Hide Procedure")
    questionnaire = fields.Boolean(default=True, help="Show/Hide Questionnaire")
    document_ref = fields.Boolean(default=True, help="Show/Hide Document Reference")
    service = fields.Boolean(default=True, help="Show/Hide Service")
    participant = fields.Boolean(default=True, help="Show/Hide Participant feature")
    careplan = fields.Boolean(default=True, help="Show/Hide Careplan feature")

    @api.onchange("admission")
    def _onchange_admission(self):
        for rec in self:
            if rec.admission:
                rec.write({"auto_close": False})

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))

    def _get_auto_close_reference_time(self, now, company):
        """Reference instant (UTC-naive, comparable to create_date) before
        which an in-progress encounter of this class is eligible to close.

        For the midnight-offset mode, the day boundary is computed in the
        encounter company's timezone (falling back to UTC), not in raw
        UTC - otherwise the cutoff drifts by the company's UTC offset,
        closing encounters early or late around local midnight.
        """
        self.ensure_one()
        if self.auto_close_midnight:
            tz_name = company.resource_calendar_id.tz or "UTC"
            tz = pytz.timezone(tz_name)
            today_local = pytz.utc.localize(now).astimezone(tz).date()
            rev_date = today_local - relativedelta(days=self.auto_close_offset_number)
            rev_local_eod = tz.localize(datetime.combine(rev_date, time.max))
            return rev_local_eod.astimezone(pytz.utc).replace(tzinfo=None)
        offset = {self.auto_close_offset_type: self.auto_close_offset_number}
        return now - relativedelta(**offset)

    @api.model
    def cron_auto_close(self):
        now = fields.Datetime.now()
        classes = self.search([("auto_close", "=", True)])
        enc_model = self.env["ni.encounter"]
        for cls in classes:
            candidates = enc_model.search(
                [("class_id", "=", cls.id), ("state", "=", "in-progress")],
                order="id",
            )
            to_close = enc_model
            for company in candidates.mapped("company_id"):
                rev = cls._get_auto_close_reference_time(now, company)
                logging.debug(
                    "%s encounter: auto-close reference time (company=%s) = %s"
                    % (cls.name, company.name, rev)
                )
                to_close |= candidates.filtered(
                    lambda e, rev=rev: e.company_id == company and e.create_date <= rev
                )
            if to_close:
                to_close.action_close()
                _logger.info("%s encounter: Closed  ids=%s" % (cls.name, to_close.ids))
            else:
                _logger.info(
                    "%s encounter: Not found any encounter to close" % cls.name
                )
