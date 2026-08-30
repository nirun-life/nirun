#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class DiagnosisRoleWizard(models.TransientModel):
    _name = "ni.encounter.diagnosis.role.wizard"
    _description = "Select Diagnosis Role"

    diagnosis_id = fields.Many2one("ni.encounter.diagnosis", required=True)
    system_id = fields.Many2one(related="diagnosis_id.system_id")
    role_id = fields.Many2one("ni.encounter.diagnosis.role", required=True)

    def action_confirm(self):
        self.diagnosis_id.write({"is_diagnosis": True, "role_id": self.role_id.id})
