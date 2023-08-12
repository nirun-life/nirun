#  Copyright (c) 2023 NSTDA
from odoo import fields, models


class EncounterClass(models.Model):
    _inherit = "ni.encounter.class"

    summary_report_title = fields.Char(default="Summary Report")

    def action_print_summary_report(self):
        return self.env.ref(
            "ni_patient_summary_report.action_report_summary"
        ).report_action(self.ids)

    def action_print_medical_certificate(self):
        return self.env.ref(
            "ni_patient_summary_report.action_report_medical_certificate"
        ).report_action(self.ids)
