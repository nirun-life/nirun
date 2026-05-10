#  Copyright (c) 2026 NSTDA
from odoo import api, fields, models


class Immunization(models.Model):
    _name = "ni.immunization"
    _description = "Immunization"
    _inherit = [
        "ni.workflow.event.mixin",
        "ni.identifier.mixin",
        "mail.thread",
    ]
    _order = "occurrence DESC, id DESC"
    _identifier_ts_field = "occurrence"

    name = fields.Char(related="vaccine_id.name", store=True)
    vaccine_id = fields.Many2one(
        "ni.immunization.vaccine", "Vaccine", required=True, tracking=True
    )
    lot_number = fields.Char(tracking=True)
    expiration_date = fields.Date(tracking=True)
    dose_quantity = fields.Float(digits=(6, 2))

    location_id = fields.Many2one("ni.location", tracking=True)
    site_id = fields.Many2one("ni.body.site", "Injection Site", tracking=True)
    route_id = fields.Many2one("ni.immunization.route", tracking=True)
    performer_id = fields.Many2one(
        "hr.employee",
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )
    note = fields.Text()

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

    @api.onchange("vaccine_id")
    def _onchange_vaccine_id(self):
        for rec in self:
            if rec.vaccine_id and rec.vaccine_id.definition:
                rec.note = rec.vaccine_id.definition
