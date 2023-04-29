#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class MedicationStatement(models.Model):
    _name = "ni.medication.statement"
    _description = "Medication Statement"
    _inherit = [
        "ni.medication.abstract",
        "ni.workflow.event.mixin",
        "mail.thread",
        "mail.activity.mixin",
    ]
    _check_period_start = True

    name = fields.Char(related="medication_id.name", store=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    category_id = fields.Many2one(
        default=lambda self: self.env.ref(
            "ni_medication.admin_location_patient_specified"
        )
    )
    condition_ids = fields.Many2many(
        "ni.condition",
        "ni_medication_statement_condition",
        "statement_id",
        "condition_id",
        help="Why medication is being/was taken",
    )
    state = fields.Selection(
        default="completed",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)

    note = fields.Text(help="Further information")

    @api.onchange("medication_id")
    def _onchange_medication_id(self):
        res = {}
        if self.medication_id and self.medication_id.condition_code_ids:
            condition = self.env["ni.condition.latest"].search(
                [("code_id", "in", self.medication_id.condition_code_ids.ids)]
            )
            res = {"value": {"condition_ids": condition.ids}}
        return res

    @api.depends("medication_id.name", "patient_id.name")
    def _compute_display_name(self):
        diff = dict(show_patient=True, show_occurrence=None, show_state=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        rec = self
        name = rec.name or rec.medication_id.name
        if self._context.get("show_patient"):
            name = "{}, {}".format(rec.patient_id._name_get(), name)
        if self._context.get("show_occurrence"):
            if rec.occurrence:
                name = "{} | {}".format(name, rec.occurrence_date)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, rec._get_state_label())
        return name

    @property
    def _workflow_summary(self):
        return "{}; {}, {}".format(
            self.category_id.name, self.medication_id.name, self.dosage_id.display_name
        )
