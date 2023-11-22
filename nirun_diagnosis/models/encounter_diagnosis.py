#  Copyright (c) 2023-2023. NSTDA

from odoo import _, api, fields, models


class Diagnosis(models.Model):
    _name = "ni.encounter.diagnosis"
    _description = "Diagnosis"

    _order = "sequence,create_date"

    @api.model
    def _get_default_seq_role(self):
        if not self.env.context.get("default_role_id"):
            return 99
        role_id = self.env.context.get("default_role_id")
        role = self.env["ni.diagnosis.role"].search([("id", "=", role_id)])
        return role.sequence * 10 if role else 99

    @api.model
    def _get_default_seq(self):
        if self.env.context.get("default_encounter_id"):
            eid = self.env.context.get("default_encounter_id")
            dx = self.env["ni.encounter.diagnosis"].search(
                [("encounter_id", "=", eid)], limit=1, order="sequence desc"
            )
            if dx:
                return dx.sequence + 1
        return self._get_default_seq_role()

    encounter_id = fields.Many2one("ni.encounter", required=True)
    sequence = fields.Integer(default=lambda self: self._get_default_seq())
    type = fields.Selection(
        [("condition", "Condition"), ("procedure", "Procedure")],
        required=True,
        default="condition",
        index=True,
    )
    role_id = fields.Many2one("ni.diagnosis.role", required=True)
    condition_id = fields.Reference(
        [("ni.condition", "Diagnosis"), ("ni.procedure", "Procedure")],
        "Condition",
        index=True,
        required=True,
        help="The diagnosis or procedure relevant to the encounter",
    )

    _sql_constraints = [
        (
            "encounter_condition_uniq",
            "unique (encounter_id, condition_id)",
            _("Condition must be unique!"),
        ),
    ]
