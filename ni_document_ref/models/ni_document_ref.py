#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models

LOCK_STATE_DICT = {
    "completed": [("readonly", True)],
    "not-done": [("readonly", True)],
    "abort": [("readonly", True)],
    "suspended": [("readonly", True)],
}


class DocumentReference(models.Model):
    _name = "ni.document.ref"
    _description = "Document Reference"
    _inherit = ["ni.workflow.event.mixin", "ni.identifier.mixin"]
    _order = "occurrence desc"
    _identifier_ts_field = "occurrence"

    @api.model
    def default_get(self, fields):
        res = super(DocumentReference, self).default_get(fields)
        if "type_id" in fields and "type_id" not in res:
            type_id = self.env.user.employee_id.job_id.document_ref_type_id.id
            res["type_id"] = type_id or None
        return res

    type_id = fields.Many2one(
        "ni.document.ref.type", index=True, required=True, states=LOCK_STATE_DICT
    )
    category_id = fields.Many2one(
        "ni.document.ref.category", related="type_id.category_id", store=True
    )
    occurrence = fields.Datetime(default=fields.Datetime.now(), index=True)
    author_id = fields.Many2one(
        "hr.employee",
        index=True,
        default=lambda self: self.env.user.employee_id,
        states=LOCK_STATE_DICT,
    )
    author_ids = fields.Many2many(
        "hr.employee", string="Co-Authors", states=LOCK_STATE_DICT
    )

    attachment_ids = fields.Many2many(
        "ir.attachment",
        required=True,
        auto_join=True,
        ondelete="cascade",
        states=LOCK_STATE_DICT,
    )
    attachment_count = fields.Integer(compute="_compute_attachment_count")
    data = fields.Html(states=LOCK_STATE_DICT)
    no_data = fields.Boolean(compute="_compute_no_data")
    state = fields.Selection(default="in-progress")
    active = fields.Boolean(default=True)

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    @api.depends("data")
    def _compute_no_data(self):
        for rec in self:
            rec.no_data = not bool(rec.data)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "author_id" in vals and vals["author_id"]:
                cmd = [fields.Command.link(vals["author_id"])]
                # Add user as co-author if author_id is not user themselves
                if (
                    vals["author_id"] != self.env.user.employee_id.id
                    and self.env.user.employee_id
                ):
                    cmd.append(fields.Command.link(self.env.user.employee_id.id))
                vals["author_ids"] = cmd

        return super(DocumentReference, self).create(vals_list)

    def action_close_dialog(self):
        return {"type": "ir.actions.act_window_close"}

    def action_print(self):
        return self.env.ref("ni_document_ref.action_report_document").report_action(
            self.ids
        )

    @api.onchange("type_id")
    def _onchange_type_id(self):
        if self.type_id.data_template:
            self.data = self.type_id.data_template

    @property
    def _workflow_name(self):
        return self._description

    @property
    def _workflow_summary(self):
        return self.type_id.name
