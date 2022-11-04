#  Copyright (c) 2022. NSTDA

from odoo import api, fields, models, tools


class Workflow(models.AbstractModel):
    _name = "ni.workflow"
    _description = "Workflow"
    _workflow_type = False
    _order = "occurrence desc, id desc"

    company_id = fields.Many2one(
        related="patient_id.company_id", store=True, readonly=True, index=True
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        index=True,
        ondelete="cascade",
        required=True,
        tracking=True,
    )
    encounter_id = fields.Many2one(
        "ni.encounter",
        "Encounter No.",
        ondelete="restrict",
        index=True,
        tracking=True,
        check_company=True,
    )
    name = fields.Char(required=True)
    summary = fields.Text()
    occurrence = fields.Datetime(index=True)
    occurrence_date = fields.Date(index=True)
    type = fields.Selection(
        [("request", "Request"), ("event", "Event")],
        required=True,
        default=lambda self: self._workflow_type,
    )

    res_model = fields.Char("Related Resource Model", copy=False)
    res_id = fields.Many2oneReference(
        "Related Resource ID", model_field="res_model", copy=False
    )

    def init(self):
        if not self._abstract:
            tools.create_index(
                self._cr,
                "{}_res_model_res_id_index".format(self._table),
                self._table,
                ["res_model", "res_id"],
            )

    @api.model
    def garbage_collect(self):
        from odoo.tools.date_utils import get_timedelta

        limit_date = fields.datetime.utcnow() - get_timedelta(1, "day")

        return self.search(
            [
                ("res_model", "=", False),
                ("res_id", "=", False),
                ("create_date", "<", limit_date),
                ("write_date", "<", limit_date),
            ]
        ).unlink()

    def action_resource(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self.res_model,
            "res_id": self.res_id,
            "views": [[False, "form"]],
            "target": "new",
        }


class Request(models.Model):
    _name = "ni.workflow.request"
    _workflow_type = "request"
    _inherit = "ni.workflow"

    parent_id = fields.Many2one("ni.workflow.request", "Base on")
    replace_id = fields.Many2one(
        "ni.workflow.request", "Replace", domain=[("is_replaced", "=", False)]
    )
    replaced_by_ids = fields.One2many(
        "ni.workflow.request", "replace_id", "Replaced by"
    )
    is_replaced = fields.Boolean(store=True, compute="_compute_is_replaced")
    event_ids = fields.One2many(
        "ni.workflow.event",
        "request_id",
    )
    event_count = fields.Integer(compute="_compute_event_count")

    @api.depends("event_ids")
    def _compute_event_count(self):
        for rec in self:
            rec.event_count = len(rec.event_ids)

    @api.depends("replaced_by_ids")
    def _compute_is_replaced(self):
        for rec in self:
            rec.is_replaced = bool(rec.replaced_by_ids)


class Event(models.Model):
    _name = "ni.workflow.event"
    _workflow_type = "event"
    _inherit = "ni.workflow"

    parent_id = fields.Many2one("ni.workflow.event", "Part of")
    request_id = fields.Many2one("ni.workflow.request", "Base on", required=False)
