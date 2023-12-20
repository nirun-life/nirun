#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EncounterParticipant(models.Model):
    _name = "ni.encounter.participant"
    _description = "Encounter Participant"
    _inherit = ["ni.period.mixin"]
    _order = "period_start desc, period_end desc, type_id"

    def _get_default_type(self):
        part = self.env.ref("ni_patient.PART")
        if part and part.active:
            return part
        else:
            return self.env["ni.participant.type"].search([], limit=1)

    encounter_id = fields.Many2one("ni.encounter", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="encounter_id.company_id")
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="restrict")
    user_id = fields.Many2one(
        "res.users",
        required=False,
        ondelete="restrict",
        store=True,
        compute="_compute_user_id",
        inverse="_inverse_user_id",
    )
    type_id = fields.Many2one(
        "ni.participant.type",
        default=lambda self: self._get_default_type(),
        required=True,
        ondelete="restrict",
    )
    period_start = fields.Datetime(required=True)
    note = fields.Text()

    _sql_constraints = [
        (
            "period_start_end_check",
            """CHECK (
                period_end is NULL or
                period_end > period_start
            )""",
            _("Participant end time must be after start time"),
        ),
    ]

    def action_stop(self):
        self.filtered_domain([("period_end", "=", False)]).write(
            {"period_end": fields.datetime.now().replace(microsecond=0)}
        )

    @api.depends("employee_id")
    def _compute_user_id(self):
        for rec in self:
            if rec.employee_id:
                rec.user_id = rec.employee_id.user_id

    def _inverse_user_id(self):
        for rec in self:
            if rec.user_id:
                rec.employee_id = rec.user_id.employee_id

    @api.constrains("employee_id", "period_start", "period_end")
    def check_interception(self):
        for rec in self:
            intercept = rec.search_intercept(
                [
                    ("encounter_id", "=", rec.encounter_id.id),
                    ("employee_id", "=", rec.employee_id.id),
                ]
            )
            if intercept:
                r = intercept[0]
                raise ValidationError(
                    _(
                        "{} already involved for given time! {}"
                        "\n\n\t{} ({} → {})".format(
                            rec.employee_id.name,
                            rec.period_start,
                            r.type_id.name,
                            r.period_start or "...",
                            r.period_end or _("Now"),
                        )
                    )
                )

    @api.constrains("period_end")
    def check_period_end(self):
        now = fields.Datetime.now()
        for rec in self.filtered_domain([("period_end", "!=", False)]):
            if rec.period_end < rec.period_start:
                raise ValidationError(_("Participant end time must be "))
            limit_date = rec.encounter_id.period_end or now
            if rec.period_end > limit_date:
                raise ValidationError(
                    _(
                        "Participant end time (%s) must not be in the"
                        " future or after the encounter have ended (%s) "
                        % (rec.period_end, limit_date)
                    )
                )
