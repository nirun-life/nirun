from odoo import _, api, fields, models


class Encounter(models.Model):
    _inherit = 'ni.encounter'

    def action_presense_link(self):
        return self.patient_id.action_presense_link()



