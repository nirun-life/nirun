#  Copyright (c) 2023 NSTDA

from odoo import api, fields, models

from odoo.addons.ni_patient.models.ni_encounter import LOCK_STATE_DICT


class Encounter(models.Model):
    _inherit = "ni.encounter"

    performer_id = fields.Many2one(
        "hr.employee",
        index=True,
        tracking=True,
        check_company=True,
        states=LOCK_STATE_DICT,
        domain="[('company_id', 'in', [company_id, False]),('department_id', '=?', department_id )]",
    )
    performer_license_id = fields.Many2one(
        "hr.resume.line",
        "License",
        tracking=True,
        states=LOCK_STATE_DICT,
        domain=[("employee_id", "=", performer_id)],
    )
    performer_license_no = fields.Char(
        related="performer_license_id.identifier", string="License No."
    )
    department_id = fields.Many2one(
        "hr.department",
        index=True,
        tracking=True,
        states=LOCK_STATE_DICT,
        check_company=True,
    )

    @api.onchange("performer_id")
    def onchange_domain(self):
        if self.performer_id.license_default_id:
            self.update(
                {"performer_license_id": self.performer_id.license_default_id.id}
            )
        elif self.performer_id and self.performer_license_id:
            if self.performer_id != self.performer_license_id.employee_id:
                self.update({"performer_license_id": None})
        if not self.department_id and self.performer_id.department_id:
            self.department_id = self.performer_id.department_id
        license_type_id = self.env.ref("ni_practitioner.resume_type_license").id
        return {
            "domain": {
                "performer_license_id": [
                    ("employee_id", "=", self.performer_id.id),
                    ("line_type_id", "=", license_type_id),
                ]
            }
        }

    @api.onchange("department_id")
    def _onchange_department_id(self):
        if self.department_id and self.performer_id:
            if self.department_id != self.performer_id.department_id:
                self.update(
                    {
                        "performer_id": None,
                        "performer_license_id": None,
                    }
                )
