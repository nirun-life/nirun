#  Copyright (c) 2026 NSTDA

from odoo import api, models


class Observation(models.Model):
    _inherit = "ni.observation"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._evaluate_flag_recommendations()
        return records

    def write(self, vals):
        result = super().write(vals)
        relevant_fields = {
            "type_id",
            "patient_id",
            "encounter_id",
            "value",
            "value_float",
            "value_int",
            "value_char",
            "value_code_id",
            "value_code_ids",
            "interpretation_id",
        }
        if result and relevant_fields.intersection(vals):
            self._evaluate_flag_recommendations()
        return result

    def _evaluate_flag_recommendations(self):
        Rule = self.env["ni.flag.recommendation.rule"]
        for observation in self.filtered(lambda rec: rec.patient_id and rec.type_id):
            rules = Rule.search(
                [
                    ("active", "=", True),
                    ("observation_type_id", "=", observation.type_id.id),
                ]
            )
            rules.evaluate_observation(observation)
