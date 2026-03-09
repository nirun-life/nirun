#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class ObservationReport(models.AbstractModel):
    _name = "ni.observation.report"
    _description = "Observation Report Abstract"
    _auto = False
    _inherit = ["ni.observation.abstract"]

    sheet_id = fields.Many2one("ni.observation.sheet", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    patient_id = fields.Many2one("ni.patient")
    encounter_id = fields.Many2one("ni.encounter")
    occurrence = fields.Datetime(readonly=True)
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")]
    )
    type_id = fields.Many2one("ni.observation.type", readonly=True, required=True)
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

    observation_id = fields.Many2one(
        "ni.observation", compute="_compute_observation", compute_sudo=True
    )

    history_ids = fields.One2many(
        "ni.observation", compute="_compute_observation", compute_sudo=True
    )
    history_count = fields.Integer(compute="_compute_observation", compute_sudo=True)

    create_date = fields.Datetime("Created on")
    create_uid = fields.Many2one("res.users", "Created by")
    write_date = fields.Datetime("Last Updated on")
    write_uid = fields.Many2one("res.users", "Last Updated by")

    def _compute_observation(self):
        for rec in self:
            obs = self.env["ni.observation"].browse(self.id)
            if obs:
                rec.update(
                    {
                        "observation_id": obs.id,
                        "history_ids": obs.history_ids,
                        "history_count": len(obs.history_ids),
                    }
                )
            else:
                rec.update(
                    {"observation_id": None, "history_ids": None, "history_count": 0}
                )

    def action_graph_view(self):
        self.ensure_one()
        return self.observation_id.view_graph()
