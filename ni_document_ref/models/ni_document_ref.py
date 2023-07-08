#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models

LOCK_STATE_DICT = {
    "completed": [("readonly", True)],
    "not-done": [("readonly", True)],
    "abort": [("readonly", True)],
}


class DocumentReference(models.Model):
    _name = "ni.document.ref"
    _description = "Document Reference"
    _inherit = ["ni.workflow.event.mixin"]

    type_id = fields.Many2one(
        "ni.document.ref.type", required=True, states=LOCK_STATE_DICT
    )
    category_id = fields.Many2one(
        "ni.document.ref.category", related="type_id.category_id", store=True
    )
    occurrence = fields.Datetime(default=fields.Datetime.now())

    attachment_ids = fields.Many2many(
        "ir.attachment",
        required=True,
        auto_join=True,
        ondelete="cascade",
        states=LOCK_STATE_DICT,
    )
    data = fields.Html(states=LOCK_STATE_DICT)
    state = fields.Selection(default="in-progress")
    active = fields.Boolean(default=True)

    def action_save_and_print(self):
        return self.env.ref("ni_document_ref.action_report_document").report_action(
            self
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
