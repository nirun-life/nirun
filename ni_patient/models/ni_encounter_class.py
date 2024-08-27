#  Copyright (c) 2021-2023 NSTDA

import logging

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

    auto_close = fields.Boolean(default=False)
    auto_close_midnight = fields.Boolean(default=True)
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

    @api.model
    def cron_auto_close(self):
        now = fields.Datetime.now()
        classes = self.search([("auto_close", "=", True)])
        enc_model = self.env["ni.encounter"]
        for cls in classes:
            if cls.auto_close_midnight:
                offset = {"days": cls.auto_close_offset_number}
                rev = now.date() - relativedelta(**offset)
            else:
                offset = {cls.auto_close_offset_type: cls.auto_close_offset_number}
                rev = now - relativedelta(**offset)
            logging.debug(
                "%s encounter: auto-close reference time = %s" % (cls.name, rev)
            )
            enc = enc_model.search(
                [
                    ("class_id", "=", cls.id),
                    ("state", "=", "in-progress"),
                    ("create_date", "<=", rev),
                ],
                order="id",
            )
            if enc:
                enc.action_close()
                _logger.info("%s encounter: Closed  ids=%s" % (cls.name, enc.ids))
            else:
                _logger.info(
                    "%s encounter: Not found any encounter to close" % cls.name
                )
