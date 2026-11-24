#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models, tools


class ConditionLatest(models.Model):
    # Plain model with an explicit column list: inheriting ni.condition over a
    # "SELECT *" tied the view to every column other modules add to the table.
    _name = "ni.condition.latest"
    _description = "Patient Current Condition"
    _auto = False

    def _condition_selection(self, field_name):
        field = self.env["ni.condition"]._fields[field_name]
        return field._description_selection(self.env)

    condition_id = fields.Many2one("ni.condition", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    patient_id = fields.Many2one("ni.patient", readonly=True)
    encounter_id = fields.Many2one("ni.encounter", readonly=True)
    name = fields.Char("Condition Name", readonly=True)
    code_id = fields.Many2one("ni.condition.code", "Condition Code", readonly=True)
    code = fields.Char(readonly=True)
    is_problem = fields.Boolean("Chronic", readonly=True)
    is_diagnosis = fields.Boolean(readonly=True)
    severity = fields.Selection(
        lambda self: self._condition_selection("severity"),
        readonly=True,
    )
    clinical_state = fields.Selection(
        lambda self: self._condition_selection("clinical_state"),
        string="Status",
        readonly=True,
    )
    verification_id = fields.Many2one("ni.condition.verification", readonly=True)
    period_start = fields.Datetime("Onset", readonly=True)
    period_end = fields.Datetime("Abatement", readonly=True)
    note = fields.Text(readonly=True)

    @api.depends("condition_id.display_name")
    @api.depends_context(
        "show_code",
        "show_patient",
        "show_severity",
        "show_state",
        "show_identifier",
        "show_identification_id",
        "show_gender_age",
        "show_age",
    )
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.condition_id.display_name

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT
                c.id,
                c.id AS condition_id,
                c.company_id,
                c.patient_id,
                c.encounter_id,
                c.name,
                c.code_id,
                c.code,
                c.is_problem,
                c.is_diagnosis,
                c.severity,
                c.clinical_state,
                c.verification_id,
                c.period_start,
                c.period_end,
                c.note,
                c.create_uid,
                c.create_date,
                c.write_uid,
                c.write_date
            FROM ni_condition c
            WHERE c.id IN (
                SELECT max(id)
                FROM ni_condition
                WHERE clinical_state IN ('active', 'recurrence', 'remission')
                GROUP BY patient_id, code_id
            )
        )
        """
            % self._table
        )
