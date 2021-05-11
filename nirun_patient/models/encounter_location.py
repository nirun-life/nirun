#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class EncounterLocation(models.Model):
    _name = "ni.encounter.location.rel"
    _description = "Location History"
    _inherit = ["period.mixin"]
    _check_company_auto = True

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        ondelete="cascade",
        index=True,
        default=lambda self: self.env.company,
    )
    encounter_id = fields.Many2one(
        "ni.encounter",
        string="Encounter",
        required=True,
        ondelete="cascade",
        index=True,
        check_company=True,
    )
    location_id = fields.Many2one(
        "ni.location",
        string="Location",
        ondelete="restrict",
        index=True,
        required=True,
        check_company=True,
    )
    physical_type_id = fields.Many2one(
        related="location_id.physical_type_id", store=False
    )
