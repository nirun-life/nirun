#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models


class WorkflowMixin(models.AbstractModel):
    _name = "ni.workflow.mixin"
    _description = "Workflow Mixin"
    _inherit = [
        "ni.patient.res",
    ]
    _workflow_occurrence_field = "occurrence"
    _workflow_type = False

    @property
    def _workflow_table(self) -> str:
        return "ni.workflow.{}".format(self._workflow_type)

    @property
    def _workflow_name(self) -> str:
        return self._description

    @property
    def _workflow_summary(self) -> str:
        return str()

    @property
    def _workflow_occurrence(self) -> fields.Datetime:
        if self._workflow_occurrence_field in self._fields:
            return self[self._workflow_occurrence_field]
        else:
            return self.create_date

    def _workflow_replace_id(self, data):
        if "replace_id" in self._fields and self.replace_id:
            data["replace_id"] = (
                self.replace_id.event_id.id
                if self._workflow_type == "event"
                else self.replace_id.request_id.id
            )

    def _to_workflow(self):
        data = {
            "company_id": self.company_id.id,
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "res_model": self._name,
            "res_id": self.id,
            "name": self._workflow_name,
            "summary": self._workflow_summary,
            "occurrence": self._workflow_occurrence,
            "type": self._workflow_type,
            "state": self.state,
            "create_date": self.create_date,
            "create_uid": self.create_uid.id,
            "write_date": self.write_date,
            "write_uid": self.write_uid.id,
        }
        if self._safe_get_parent():
            data["parent_id"] = self._safe_get_parent().id
        self._workflow_replace_id(data)
        return data

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec._write_workflow()
        return records

    def write(self, vals):
        success = super().write(vals)
        for rec in self:
            rec._write_workflow()
        return success

    def _write_workflow(self):
        self.ensure_one()
        rec = self
        workflow_id = "%s_id" % self._workflow_type
        if rec[workflow_id]:
            rec[workflow_id].write(rec._to_workflow())
        else:
            rec[workflow_id] = self.env[self._workflow_table].create(rec._to_workflow())

    def unlink(self):
        """Override unlink to delete workflow. This cannot be
        cascaded, because link is done through (res_model, res_id)."""
        record_ids = self.ids
        result = super(WorkflowMixin, self).unlink()
        self.env[self._workflow_table].sudo().search(
            [("res_model", "=", self._name), ("res_id", "in", record_ids)]
        ).unlink()
        return result

    def _get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    def _safe_get_parent(self):
        if "parent_id" in self._fields and self.parent_id:
            return self.partner_id
        else:
            return None


class EventMixin(models.AbstractModel):
    _name = "ni.workflow.event.mixin"
    _description = "Event Mixin"
    _inherit = "ni.workflow.mixin"
    _workflow_type = "event"

    event_id = fields.Many2one(
        "ni.workflow.event",
        "Event",
        auto_join=True,
        ondelete="cascade",
        domain=[
            ("res_model", "=", lambda self: self._name),
            ("res_id", "=", lambda self: self.id),
        ],
    )

    state = fields.Selection(
        related="event_id.state", readonly=False, store=True, default="preparation"
    )
    occurrence = fields.Datetime(
        related="event_id.occurrence",
        readonly=False,
        store=True,
        default=fields.Datetime.now(),
    )
    occurrence_date = fields.Date(
        related="event_id.occurrence_date", readonly=False, store=True
    )

    @property
    def _workflow_request_id(self):
        return None

    def _to_workflow(self):
        res = super(EventMixin, self)._to_workflow()
        if self._workflow_request_id:
            res.update({"request_id": self._workflow_request_id.id})
        return res

    def action_not_done(self):
        self.filtered_domain([("state", "=", "preparation")]).write(
            {"state": "not-done"}
        )

    def action_start(self):
        self.filtered_domain([("state", "=", "preparation")]).write(
            {"state": "in-progress"}
        )

    def action_suspend(self):
        self.filtered_domain([("state", "=", "in-progress")]).write(
            {"state": "suspended"}
        )

    def action_resume(self):
        self.filtered_domain([("state", "=", "suspended")]).write(
            {"state": "in-progress"}
        )

    def action_complete(self):
        self.filtered_domain([("state", "in", ["preparation", "in-progress"])]).write(
            {"state": "completed"}
        )

    def action_abort(self):
        self.filtered_domain([("state", "in", "in-progress")]).write({"state": "abort"})


class RequestMixin(models.AbstractModel):
    _name = "ni.workflow.request.mixin"
    _description = "Request Mixin"
    _inherit = "ni.workflow.mixin"
    _workflow_type = "request"
    _workflow_occurrence_field = "create_date"

    request_id = fields.Many2one(
        "ni.workflow.request",
        "Request",
        auto_join=True,
        ondelete="cascade",
        readonly=True,
        domain=[
            ("res_model", "=", lambda self: self._name),
            ("res_id", "=", lambda self: self.id),
        ],
    )
    priority = fields.Selection(related="request_id.priority", readonly=False)
    intent = fields.Selection(related="request_id.intent", readonly=False, store=True)
    state = fields.Selection(
        related="request_id.state", readonly=False, store=True, default="draft"
    )

    def _to_workflow(self):
        data = super(RequestMixin, self)._to_workflow()
        data.update(
            {
                "priority": self.priority or "routine",
                "intent": self.intent or "order",
            }
        )
        return data

    def action_confirm(self):
        self.filtered_domain([("state", "=", "draft")]).write({"state": "active"})

    def action_hold(self):
        self.filtered_domain([("state", "=", "active")]).write({"state": "on-hold"})

    def action_resume(self):
        self.filtered_domain([("state", "=", "on-hold")]).write({"state": "active"})

    def action_complete(self):
        self.filtered_domain([("state", "in", ["draft", "active"])]).write(
            {"state": "completed"}
        )

    def action_revoked(self):
        self.filtered_domain([("state", "in", "in-progress")]).write(
            {"state": "revoked"}
        )
