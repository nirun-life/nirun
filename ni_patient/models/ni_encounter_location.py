#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class EncounterLocation(models.Model):
    _name = "ni.encounter.location"
    _description = "Location History"
    _inherit = ["ni.period.mixin"]
    _check_company_auto = True

    company_id = fields.Many2one(
        related="encounter_id.company_id",
        store=True,
        precompute=True,
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
        related="location_id.physical_type_id",
        store=True,
        precompute=True,
    )
    note = fields.Text()
