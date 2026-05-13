#  Copyright (c) 2026 NSTDA
from odoo import _, api, fields, models


class Immunization(models.Model):
    _name = "ni.immunization"
    _description = "Immunization"
    _inherit = [
        "ni.workflow.event.mixin",
        "ni.identifier.mixin",
    ]
    _order = "occurrence DESC, id DESC"
    _identifier_ts_field = "occurrence"

    name = fields.Char(related="vaccine_id.name", store=True)
    vaccine_id = fields.Many2one(
        "ni.immunization.vaccine", "Vaccine", required=True, tracking=True
    )
    vaccine_route_id = fields.Many2one(related="vaccine_id.route_id")
    lot_number = fields.Char(tracking=True)
    expiration_date = fields.Date(tracking=True)
    dose_quantity = fields.Float(digits=(6, 2))

    location_id = fields.Many2one("ni.location", tracking=True)
    route_id = fields.Many2one(
        "ni.immunization.route",
        tracking=True,
        domain="[('id', '=', vaccine_route_id)] if vaccine_route_id else []",
    )
    route_site_ids = fields.Many2many(related="route_id.site_ids")
    site_id = fields.Many2one(
        "ni.body.site",
        "Injection Site",
        tracking=True,
        domain="[('id', 'in', route_site_ids)] if route_site_ids else []",
    )
    performer_id = fields.Many2one(
        "hr.employee",
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )
    state = fields.Selection(default="completed")
    note = fields.Text()

    evaluation_ids = fields.One2many("ni.immunization.evaluation", "immunization_id")
    evaluation_count = fields.Integer(compute="_compute_evaluation_count")
    pending_disease_ids = fields.Many2many(
        "ni.immunization.target.disease",
        compute="_compute_pending",
    )
    pending_disease_count = fields.Integer(compute="_compute_pending")

    def init(self):
        self.env.cr.execute(
            """
            CREATE INDEX IF NOT EXISTS ni_immunization_encounter_idx
            ON ni_immunization (company_id, encounter_id)
            WHERE encounter_id IS NOT NULL
            """
        )

    def _compute_evaluation_count(self):
        for rec in self:
            rec.evaluation_count = len(rec.evaluation_ids)

    @api.depends("vaccine_id.target_disease_ids", "evaluation_ids.target_disease_id")
    def _compute_pending(self):
        for rec in self:
            evaluated = rec.evaluation_ids.mapped("target_disease_id")
            rec.pending_disease_ids = rec.vaccine_id.target_disease_ids - evaluated
            rec.pending_disease_count = len(rec.pending_disease_ids)

    def action_evaluate(self):
        self.ensure_one()
        if len(self.pending_disease_ids) > 1:
            return self._action_evaluate_wizard()
        ctx = {
            "default_patient_id": self.patient_id.id,
            "default_encounter_id": self.encounter_id.id,
            "default_immunization_id": self.id,
        }
        if self.pending_disease_ids:
            ctx["default_target_disease_id"] = self.pending_disease_ids.id
        return {
            "type": "ir.actions.act_window",
            "name": _("Add Evaluation"),
            "res_model": "ni.immunization.evaluation",
            "view_mode": "form",
            "target": "new",
            "context": ctx,
        }

    def _action_evaluate_wizard(self):
        self.ensure_one()
        Evaluation = self.env["ni.immunization.evaluation"]
        imm_date = self.occurrence.date() if self.occurrence else False
        lines = []
        for disease in self.pending_disease_ids:
            prior_count = Evaluation.search_count(
                [
                    ("patient_id", "=", self.patient_id.id),
                    ("target_disease_id", "=", disease.id),
                ]
            )
            lines.append(
                fields.Command.create(
                    {
                        "target_disease_id": disease.id,
                        "dose_number": prior_count + 1,
                        "series_doses": disease.series_doses,
                        "occurrence": imm_date,
                    }
                )
            )
        wizard = self.env["ni.immunization.evaluation.wizard"].create(
            {
                "encounter_id": self.encounter_id.id,
                "immunization_id": self.id,
                "disease_ids": [fields.Command.set(self.pending_disease_ids.ids)],
                "state": "2",
                "line_ids": lines,
            }
        )
        return wizard._reopen()

    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            args += ["|", ("name", operator, name), ("identifier", operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        rec = self
        name = rec.name or rec.vaccine_id.name
        if self._context.get("show_patient"):
            name = "{}: {}".format(rec.patient_id._name_get(), name)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, rec._get_state_label())
        if self._context.get("show_identifier"):
            name = "{} - {}".format(name, rec.identifier)
        return name

    @property
    def _workflow_name(self):
        return self.vaccine_id.name

    @property
    def _workflow_summary(self):
        parts = []
        if self.route_id:
            route = self.route_id.abbr or self.route_id.name
            parts.append(f"{route} · {self.site_id.name}" if self.site_id else route)
        if self.lot_number:
            parts.append(self.lot_number)
        if self.performer_id:
            parts.append(self.performer_id.name)
        return " · ".join(parts)

    @api.onchange("vaccine_id")
    def _onchange_vaccine_id(self):
        for rec in self:
            if rec.vaccine_id:
                if rec.vaccine_id.route_id:
                    rec.site_id = False
                    rec.route_id = rec.vaccine_id.route_id

    @api.onchange("route_id")
    def _onchange_route_id(self):
        for rec in self.filtered("route_id"):
            if rec.site_id and rec.site_id not in rec.route_id.site_ids:
                rec.site_id = False
            if not rec.site_id and len(rec.route_id.site_ids) == 1:
                rec.site_id = rec.route_id.site_ids[0]
