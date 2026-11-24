#  Copyright (c) 2023. NSTDA
from odoo import api, fields, models
from odoo.fields import Command


class Communication(models.Model):
    _name = "ni.communication"
    _description = "Communication"
    _inherit = [
        "ni.workflow.event.mixin",
        "ni.identifier.mixin",
        "ni.period.mixin",
    ]
    _order = "period_start DESC"
    _identifier_ts_field = "period_start"
    _workflow_occurrence_field = "period_start"
    _rec_names_search = ["category_id.name", "identifier"]

    @api.model
    def default_get(self, fields):
        if self.env.context.get("default_patient_id"):
            pat = self.env["ni.patient"].browse(self.env.context["default_patient_id"])
            self = self.with_context(
                default_recipient_ids=[Command.link(pat[0].partner_id.id)]
            )
        if self.env.context.get("default_encounter_id"):
            enc = self.env["ni.encounter"].browse(
                self.env.context["default_encounter_id"]
            )
            if "performer_id" in enc._fields and enc[0].performer_id:
                self = self.with_context(
                    default_sender_employee_id=enc[0].performer_id.id
                )
        return super().default_get(fields)

    @api.model
    def _get_default_category(self):
        category = self.env["ni.communication.category"].search([], limit=1)
        return category.id

    category_id = fields.Many2one(
        "ni.communication.category",
        required=True,
        index=True,
        default=_get_default_category,
    )
    occurrence = fields.Datetime(related="period_start", default=None)
    period_start = fields.Datetime("Sent")
    period_end = fields.Datetime("Received")
    duration_hours = fields.Float(default=0.05)
    content_ids = fields.Many2many(
        "ni.communication.content", domain="[('category_id', '=', category_id)]"
    )

    sender_employee_id = fields.Many2one(
        "hr.employee", index=True, default=lambda self: self.env.user.employee_id
    )
    sender_id = fields.Many2one(
        "res.partner", index=True, default=lambda self: self.env.user.partner_id
    )
    recipient_ids = fields.Many2many("res.partner")

    note = fields.Text(help="Further Information")
    state = fields.Selection(default="completed")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._prepare_sender_id(vals)

        return super().create(vals_list)

    def write(self, vals):
        self._prepare_sender_id(vals)
        return super().write(vals)

    @api.model
    def _prepare_sender_id(self, vals):
        if vals.get("sender_employee_id"):
            emp_id = self.env["hr.employee"].sudo().browse(vals["sender_employee_id"])
            employee_partner_ids = [
                emp_id.user_partner_id,
                emp_id.work_contact_id,
            ]
            for partner_id in employee_partner_ids:
                if partner_id:
                    vals["sender_id"] = partner_id.id
                    break
        return vals

    @api.depends("category_id.name", "patient_id.display_name", "state", "identifier")
    @api.depends_context(
        "show_patient",
        "show_state",
        # of the patient name
        "show_identifier",
        "show_identification_id",
        "show_gender_age",
        "show_age",
    )
    def _compute_display_name(self):
        for communication in self:
            communication.display_name = communication._name_get()

    def _name_get(self):
        commu = self
        name = commu.category_id.name
        if self.env.context.get("show_patient"):
            name = f"{commu.patient_id._name_get()}: {name}"
        if self.env.context.get("show_state"):
            name = f"{name} ({commu._get_state_label()})"
        if self.env.context.get("show_identifier"):
            name = f"{name} - {commu.identifier}"
        return name

    @property
    def _workflow_summary(self):
        res = self.category_id.name
        if self.content_ids:
            payload = [c.name for c in self.content_ids]
            res = "{}; {}".format(res, ", ".join(payload))
        return res

    @api.onchange("category_id")
    def _onchange_category_id(self):
        if self.category_id:
            self.content_ids = [fields.Command.clear()]
