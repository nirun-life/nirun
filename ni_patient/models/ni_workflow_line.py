#  Copyright (c) 2026 NSTDA

from odoo import fields, models, tools


class WorkflowLine(models.Model):
    _name = "ni.workflow.line"
    _description = "Workflow Timeline"
    _auto = False
    _order = "occurrence desc"

    company_id = fields.Many2one("res.company", readonly=True)
    patient_id = fields.Many2one("ni.patient", readonly=True)
    encounter_id = fields.Many2one("ni.encounter", readonly=True)
    name = fields.Char(readonly=True)
    summary = fields.Text(readonly=True)
    occurrence = fields.Datetime(readonly=True)
    type = fields.Selection([("request", "Request"), ("event", "Event")], readonly=True)
    state = fields.Selection(
        [
            ("preparation", "Preparation"),
            ("in-progress", "In Progress"),
            ("not-done", "Not done"),
            ("suspended", "Suspend"),
            ("abort", "Aborted"),
            ("draft", "Draft"),
            ("active", "Active"),
            ("on-hold", "On-Hold"),
            ("revoked", "Revoked"),
            ("completed", "Completed"),
        ],
        readonly=True,
    )
    res_model = fields.Char(readonly=True)
    res_id = fields.Integer(readonly=True)
    create_uid = fields.Many2one("res.users", "Created by", readonly=True)
    create_date = fields.Datetime("Created on", readonly=True)
    write_uid = fields.Many2one("res.users", "Last Updated by", readonly=True)
    write_date = fields.Datetime("Last Updated on", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(
            """
            CREATE OR REPLACE VIEW ni_workflow_line AS (
                SELECT
                    e.id                    AS id,
                    e.company_id,
                    e.patient_id,
                    e.encounter_id,
                    e.name,
                    e.summary,
                    e.occurrence,
                    e.type,
                    e.state,
                    e.res_model,
                    e.res_id,
                    e.create_uid,
                    e.create_date,
                    e.write_uid,
                    e.write_date
                FROM ni_workflow_event e
                UNION ALL
                SELECT
                    r.id + 1000000000       AS id,
                    r.company_id,
                    r.patient_id,
                    r.encounter_id,
                    r.name,
                    r.summary,
                    r.occurrence,
                    r.type,
                    r.state,
                    r.res_model,
                    r.res_id,
                    r.create_uid,
                    r.create_date,
                    r.write_uid,
                    r.write_date
                FROM ni_workflow_request r
                WHERE r.is_replaced = FALSE
            )
        """
        )

    def action_resource(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        return {
            "type": "ir.actions.act_window",
            "res_model": self.res_model,
            "res_id": self.res_id,
            "views": [[False, "form"]],
            "target": "current",
            "context": ctx,
        }
