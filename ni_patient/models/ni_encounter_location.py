#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EncounterLocation(models.Model):
    _name = "ni.encounter.location"
    _description = "Location History"
    _inherit = ["ni.period.mixin"]
    _check_company_auto = True

    company_id = fields.Many2one(
        related="encounter_id.company_id",
        store=True,
        precompute=True,
    )
    encounter_id = fields.Many2one(
        "ni.encounter",
        string="Encounter",
        required=True,
        ondelete="cascade",
        index=True,
        check_company=True,
    )
    location_id = fields.Many2one(
        "ni.location",
        string="Location",
        ondelete="restrict",
        index=True,
        required=True,
        check_company=True,
    )
    physical_type_id = fields.Many2one(
        related="location_id.physical_type_id",
        store=True,
        precompute=True,
    )
    note = fields.Text()

    _period_start_end_check = models.Constraint(
        "CHECK (\n                period_end is NULL or\n                period_end > period_start\n            )",
        "Participant end time must be after start time",
    )

    def action_stop(self, dt=None):
        period_end = dt or fields.Datetime.now()
        self.filtered_domain([("period_end", "=", False)]).write(
            {"period_end": period_end.replace(microsecond=0)}
        )

    @api.constrains("period_end")
    def check_period_end(self):
        now = fields.Datetime.now()
        for rec in self.filtered_domain([("period_end", "!=", False)]):
            limit_date = rec.encounter_id.period_end or now
            if rec.period_end > limit_date:
                raise ValidationError(
                    _(
                        "Participant end time (%(end)s) must not be in the"
                        " future or after the encounter have ended (%(limit)s) ",
                        end=rec.period_end,
                        limit=limit_date,
                    )
                )
