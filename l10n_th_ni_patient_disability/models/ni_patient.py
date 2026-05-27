#  Copyright (c) 2026 NSTDA

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    disability_observation_ids = fields.One2many(
        "ni.observation",
        "patient_id",
        domain=[("category_id.code", "=", "disability")],
        string="Disability Observations",
    )
    has_disability = fields.Boolean(
        compute="_compute_disability",
        store=True,
        index=True,
    )
    disability_type_ids = fields.Many2many(
        "ni.observation.value.code",
        "ni_patient_disability_type_rel",
        "patient_id",
        "value_code_id",
        string="Disability Types",
        compute="_compute_disability",
        store=True,
    )

    @api.depends(
        "disability_observation_ids.value_code_id",
        "disability_observation_ids.value_code_ids",
        "disability_observation_ids.state",
        "disability_observation_ids.occurrence",
    )
    def _compute_disability(self):
        IrModel = self.env["ir.model.data"]
        status_type_id = IrModel._xmlid_to_res_id(
            "l10n_th_ni_patient_disability.type_disability_status"
        )
        type_type_id = IrModel._xmlid_to_res_id(
            "l10n_th_ni_patient_disability.type_disability_type_th"
        )
        disabled_id = IrModel._xmlid_to_res_id("l10n_th_ni_patient_disability.disabled")
        active_states = ("preparation", "in-progress", "completed")

        for rec in self:
            status_obs = rec.disability_observation_ids.filtered(
                lambda o: o.type_id.id == status_type_id and o.state in active_states
            ).sorted("occurrence", reverse=True)
            rec.has_disability = bool(status_obs) and (
                status_obs[0].value_code_id.id == disabled_id
            )

            type_obs = rec.disability_observation_ids.filtered(
                lambda o: o.type_id.id == type_type_id and o.state in active_states
            ).sorted("occurrence", reverse=True)
            rec.disability_type_ids = type_obs[0].value_code_ids if type_obs else []
