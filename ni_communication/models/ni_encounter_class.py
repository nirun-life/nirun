from odoo import fields, models


class EncounterClass(models.Model):
    _inherit = "ni.encounter.class"

    communication = fields.Boolean(default=True, help="Show/Hide Communication feature")
