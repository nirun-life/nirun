#  Copyright (c) 2022 Piruin P.

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError


class EncounterObservationLatest(models.Model):
    _name = "ni.encounter.observation"
    _description = "Encounter Latest Observation"
    _auto = False
    _order = "occurrence desc"
    _inherit = ["ni.observation.abstract"]

    sheet_id = fields.Many2one("ni.observation.sheet", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    patient_id = fields.Many2one("ni.patient", readonly=True)
    encounter_id = fields.Many2one("ni.encounter")
    occurrence = fields.Datetime(readonly=True)
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")]
    )
    type_id = fields.Many2one("ni.observation.type", readonly=True)
    sequence = fields.Integer(related="type_id.sequence", readonly=True)
    category_id = fields.Many2one(related="type_id.category_id", readonly=True)
    value_type = fields.Selection(
        [("char", "Char"), ("float", "Float"), ("int", "Integer"), ("code_id", "Code")],
        readonly=True,
    )
    value = fields.Char(readonly=True)
    value_char = fields.Char(readonly=True)
    value_int = fields.Integer(group_operator="avg", readonly=True)
    value_float = fields.Float(group_operator="avg", readonly=True)
    value_code_id = fields.Many2one("ni.observation.value.code", readonly=True)
    unit_id = fields.Many2one(related="type_id.unit_id")
    interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        readonly=True,
    )
    is_problem = fields.Boolean(readonly=True)
    display_class = fields.Selection(
        related="interpretation_id.display_class",
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT *
            FROM ni_observation
            WHERE id IN (
                SELECT max(id)
                FROM ni_observation
                WHERE value IS NOT NULL
                GROUP BY encounter_id, type_id
            )
        )
        """
            % (self._table)
        )

    def action_graph_view(self):
        self.ensure_one()
        return self._get_observation().view_graph()

    def _get_observation(self):
        line_id = self.env["ni.observation"].browse(self.id)
        if not line_id:
            raise ValidationError(_("Not found observation!"))
        return line_id
