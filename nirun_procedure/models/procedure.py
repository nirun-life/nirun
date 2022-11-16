#  Copyright (c) 2022. NSTDA
from odoo import api, fields, models


class Procedure(models.Model):
    _name = "ni.procedure"
    _description = "Procedure"
    _inherit = ["ni.workflow.event.mixin", "ir.sequence.mixin", "mail.thread"]
    _order = "performed_date DESC,id DESC"
    _workflow_occurrence = "performed"

    _sequence_ts_field = "performed_date"
    name = fields.Char(
        "Identifier", default=lambda self: self._sequence_default, tracking=True
    )
    code_id = fields.Many2one("ni.procedure.code", tracking=True)
    category_id = fields.Many2one("ni.procedure.category", tracking=True)
    performed_date = fields.Date(compute="_compute_performed_date", store=True)
    performed = fields.Datetime(
        required=True, default=lambda _: fields.Datetime.now(), tracking=True
    )
    state = fields.Selection(
        [
            ("preparation", "Prepation"),
            ("in-progress", "In Progress"),
            ("on-hold", "On Hold"),
            ("stopped", "Stopped"),
            ("completed", "Completed"),
        ],
        default="preparation",
        tracking=True,
    )
    location_id = fields.Many2one("ni.location", tracking=True)
    outcome_id = fields.Many2one("ni.procedure.outcome", tracking=True)
    note = fields.Html()

    @api.depends("performed")
    def _compute_performed_date(self):
        for rec in self:
            rec.performed_date = rec.performed.date()

    @api.onchange("code_id")
    def onchange_code(self):
        for rec in self:
            if rec.code_id.category_id:
                rec.category_id = rec.code_id.category_id

    def action_completed(self):
        self.write({"state": "completed"})

    def action_start(self):
        self.write({"state": "in-progress"})

    def action_stop(self):
        self.write({"state": "stopped"})

    def action_pause(self):
        self.write({"state": "on-hold"})

    @property
    def _workflow_name(self):
        return self.code_id.name

    @property
    def _workflow_summary(self):
        res = self.outcome_id.name or self.name
        if self.note:
            "%s; %s".format(res, self.note)
        return res
