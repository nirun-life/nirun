#  Copyright (c) 2026 NSTDA
from odoo import models


class ObservationReport(models.AbstractModel):
    _inherit = "ni.observation.report"

    def action_survey_monthly_pivot(self):
        return self.survey_response_id.action_monthly_pivot_view()
