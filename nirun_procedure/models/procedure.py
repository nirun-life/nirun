#  Copyright (c) 2022-2023. NSTDA
from odoo import api, fields, models


class Procedure(models.Model):
    _name = "ni.procedure"
    _description = "Procedure"
    _inherit = ["ni.workflow.event.mixin", "ir.sequence.mixin", "mail.thread"]
    _order = "performed_date DESC,id DESC"
    _workflow_occurrence = "performed"
    _sequence_field = "identifier"

    _sequence_ts_field = "performed_date"
    name = fields.Char(related="code_id.name", store=True)
    code_id = fields.Many2one("ni.procedure.code", "Procedure", tracking=True)
    identifier = fields.Char(default=lambda self: self._sequence_default, required=True)
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

    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += ["|", ("name", operator, name), ("identifier", operator, name)]
        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(ids).with_user(name_get_uid))

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        procedure = self
        name = procedure.name or procedure.code_id.name
        if self._context.get("show_category") and procedure.category_id:
            name = "{},{}".format(procedure.category_id.name, name)
        if self._context.get("show_code") and procedure.code_id.code:
            name = "[{}] {}".format(name, procedure.code_id.code)
        if self._context.get("show_patient"):
            name = "{}: {}".format(procedure.patient_id._name_get(), name)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, procedure._get_state_label())
        if self._context.get("show_identifier"):
            name = "{} - {}".format(name, procedure.identifier)
        return name

    def _get_state_label(self, vals):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

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
