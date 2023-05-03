#  Copyright (c) 2022-2023 NSTDA

from odoo import fields, models

from odoo.addons.ni_patient.models.ni_encounter import LOCK_STATE_DICT


class Encounter(models.Model):
    _inherit = "ni.encounter"

    document_ids = fields.One2many(
        "ni.document.ref", "encounter_id", states=LOCK_STATE_DICT
    )
