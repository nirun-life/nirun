#  Copyright (c) 2022 Piruin P.

from odoo import fields, models


class CareplanGoal(models.Model):
    _inherit = "ni.careplan.template"

    # solve conflict of those survey fields inherited from ni.careplan
    survey_ids = fields.Many2many(
        relation="ni_careplan_template_survey_rel",
        compute=False,
        store=False,
        copy=False,
    )
    survey_pre_response_ids = fields.Many2many(
        relation="ni_careplan_template_survey_pre_response_rel", store=False, copy=False
    )
    survey_post_response_ids = fields.Many2many(
        relation="ni_careplan_template_survey_post_response_rel",
        store=False,
        copy=False,
        readonly=True,
    )
