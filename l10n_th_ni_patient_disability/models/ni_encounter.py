#  Copyright (c) 2026 NSTDA

from odoo import models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "priority" not in fields_list:
            return res
        pat_id = res.get("patient_id") or self.env.context.get("default_patient_id")
        if not pat_id:
            return res
        patient = self.env["ni.patient"].browse(pat_id)
        if patient.has_disability:
            prio = patient.company_id.disability_encounter_priority
            if prio:
                res["priority"] = prio
        return res
