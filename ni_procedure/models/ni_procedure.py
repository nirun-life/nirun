#  Copyright (c) 2022-2023. NSTDA
from odoo import api, fields, models


class Procedure(models.Model):
    _name = "ni.procedure"
    _description = "Procedure"
    _inherit = [
        "ni.workflow.event.mixin",
        "ni.identifier.mixin",
        "mail.thread",
        "ni.period.mixin",
    ]
    _order = "occurrence DESC,id DESC"
    _identifier_ts_field = "period_start"
    _workflow_occurrence_field = "period_start"
    _rec_names_search = ["name", "identifier"]

    name = fields.Char(related="code_id.name")
    code_id = fields.Many2one("ni.procedure.code", "Procedure", tracking=True)
    code = fields.Char(related="code_id.code")
    category_id = fields.Many2one(
        related="code_id.category_id", tracking=True, store=True
    )

    location_id = fields.Many2one("ni.location", tracking=True)
    outcome_id = fields.Many2one(
        "ni.procedure.outcome",
        tracking=True,
    )
    outcome_display_class = fields.Selection(related="outcome_id.display_class")
    note = fields.Text(help="Further Information")
    performer_id = fields.Many2one(
        "hr.employee", required=True, default=lambda self: self.env.user.employee_id
    )

    @api.depends(
        "name",
        "code_id.name",
        "code_id.code",
        "category_id.name",
        "patient_id.display_name",
        "state",
        "identifier",
    )
    @api.depends_context(
        "show_category",
        "show_code",
        "show_patient",
        "show_state",
        # of the patient name
        "show_identifier",
        "show_identification_id",
        "show_gender_age",
        "show_age",
    )
    def _compute_display_name(self):
        for procedure in self:
            procedure.display_name = procedure._name_get()

    def _name_get(self):
        procedure = self
        name = procedure.name or procedure.code_id.name
        if self.env.context.get("show_category") and procedure.category_id:
            name = f"{procedure.category_id.name},{name}"
        if self.env.context.get("show_code") and procedure.code_id.code:
            name = f"[{name}] {procedure.code_id.code}"
        if self.env.context.get("show_patient"):
            name = f"{procedure.patient_id._name_get()}: {name}"
        if self.env.context.get("show_state"):
            name = f"{name} ({procedure._get_state_label()})"
        if self.env.context.get("show_identifier"):
            name = f"{name} - {procedure.identifier}"
        return name

    @api.onchange("code_id")
    def onchange_code(self):
        for rec in self:
            if rec.code_id.duration_hours:
                rec.duration_hours = rec.code_id.duration_hours

    @property
    def _workflow_name(self):
        return self.code_id.name

    @property
    def _workflow_summary(self):
        res = self.outcome_id.name or self.name
        if self.note:
            res = f"{res}; {self.note}"
        return res
