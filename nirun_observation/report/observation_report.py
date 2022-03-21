#  Copyright (c) 2022 Piruin P.

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError


class EncounterObservationLineLatest(models.Model):
    _name = "ni.encounter.observation.line"
    _auto = False
    _order = "sequence"

    observation_id = fields.Many2one("ni.observation", readonly=True)
    company_id = fields.Many2one(related="observation_id.company_id", readonly=True)
    patient_id = fields.Many2one(related="observation_id.patient_id", readonly=True)
    encounter_id = fields.Many2one(related="patient_id.encounter_id")
    effective_date = fields.Datetime(
        related="observation_id.effective_date", readonly=True
    )
    type_id = fields.Many2one("ni.observation.type", readonly=True, required=True)
    sequence = fields.Integer(related="type_id.sequence", readonly=True)
    category_id = fields.Many2one(related="type_id.category_id", readonly=True)
    value = fields.Float(group_operator="avg", readonly=True)
    unit = fields.Many2one(related="type_id.unit")
    interpretation_id = fields.Many2one("ni.observation.interpretation", readonly=True,)
    display_class = fields.Selection(related="interpretation_id.display_class",)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT *
            FROM ni_observation_line
            WHERE id IN (
                SELECT max(id)
                FROM ni_observation_line
                WHERE value IS NOT NULL
                GROUP BY encounter_id, type_id
            )
        )
        """
            % (self._table)
        )

    def action_graph_view(self):
        self.ensure_one()
        return self._get_observation_line().view_graph()

    def _get_observation_line(self):
        line_id = self.env["ni.observation.line"].browse(self.id)
        if not line_id:
            raise ValidationError(_("Not found observation!"))
        return line_id
