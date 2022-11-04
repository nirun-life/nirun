from typing import Optional

from odoo import api, fields, models


class WorkflowMixin(models.AbstractModel):
    _name = "ni.workflow.mixin"
    _description = "Workflow Mixin"
    _inherit = "ni.patient.res"
    _workflow_occurrence = "occurrence"
    _workflow_type = False

    @property
    def _workflow_table(self):
        return "ni.workflow.{}".format(self._workflow_type)

    @property
    def _workflow_name(self) -> str:
        return self._description

    @property
    def _workflow_summary(self) -> Optional[str]:
        return None

    @property
    def _workflow_occurence(self) -> fields.Datetime:
        return self.mapped(self._workflow_occurrence)[0]

    def _to_workflow(self):
        return {
            "company_id": self.company_id.id,
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "res_model": self._name,
            "res_id": self.id,
            "name": self._workflow_name,
            "summary": self._workflow_summary,
            "occurrence": self._workflow_occurence,
            "type": self._workflow_type,
            "create_date": self.create_date,
            "create_uid": self.create_uid.id,
            "write_date": self.write_date,
            "write_uid": self.write_uid.id,
        }

    @api.model
    def create(self, vals):
        record = super(WorkflowMixin, self).create(vals)
        record._write_workflow()
        return record

    def write(self, vals):
        success = super(WorkflowMixin, self).write(vals)
        for rec in self:
            rec._write_workflow()
        return success

    def _write_workflow(self):
        self.ensure_one()
        rec = self
        field_name = "%s_id" % self._workflow_type
        if rec[field_name]:
            rec[field_name].write(rec._to_workflow())
        else:
            rec[field_name] = self.env[self._workflow_table].create(rec._to_workflow())

    def unlink(self):
        """Override unlink to delete workflow. This cannot be
        cascaded, because link is done through (res_model, res_id)."""
        record_ids = self.ids
        result = super(WorkflowMixin, self).unlink()
        self.env[self._workflow_table].sudo().search(
            [("res_model", "=", self._name), ("res_id", "in", record_ids)]
        ).unlink()
        return result


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
        tracking=True,
        domain=[
            ("res_model", "=", lambda self: self._name),
            ("res_id", "=", lambda self: self.id),
        ],
    )

    @property
    def _workflow_request_id(self):
        return None

    def _to_workflow(self):
        res = super(EventMixin, self)._to_workflow()
        if self._workflow_request_id:
            res.update({"request_id": self._workflow_request_id.id})
        return res


class RequestMixin(models.AbstractModel):
    _name = "ni.workflow.request.mixin"
    _description = "Request Mixin"
    _inherit = "ni.workflow.mixin"
    _workflow_type = "request"

    request_id = fields.Many2one(
        "ni.workflow.request",
        "Request",
        auto_join=True,
        ondelete="cascade",
        readonly=True,
        tracking=True,
        domain=[
            ("res_model", "=", lambda self: self._name),
            ("res_id", "=", lambda self: self.id),
        ],
    )
