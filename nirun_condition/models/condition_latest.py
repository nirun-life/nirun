#  Copyright (c) 2021 NSTDA

from odoo import fields, models, tools


class ConditionLatest(models.Model):
    _name = "ni.condition.latest"
    _description = "Patient Current Condition"
    _inherit = ["ni.condition", "period.mixin"]
    _auto = False

    category = fields.Selection(readonly=True)
    patient_id = fields.Many2one(readonly=True, index=True)
    code_id = fields.Many2one(readonly=True, required=True, index=True)
    type_id = fields.Many2one(readonly=True)
    encounter_id = fields.Many2one(readonly=True)
    period_start = fields.Date(readonly=True)
    period_end = fields.Date(readonly=True)
    state = fields.Selection(readonly=True)
    severity = fields.Selection(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
           SELECT *
            FROM ni_condition
            WHERE id IN (
                SELECT max(id)
                FROM ni_condition
                WHERE state IN ('active', 'recurrence', 'remission')
                GROUP BY patient_id, code_id
            )
        )
        """
            % self._table
        )
