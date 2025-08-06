#  Copyright (c) 2023. NSTDA
import pprint

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from .presense_token import presense_token_encode


class Patient(models.Model):
    _inherit = "ni.patient"

    def action_presense_link(self):
        self.ensure_one()
        presense_secrets = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("presense.secret", "fXAhj78KE-sPmGIiMcKSEJ0r?uB6Ko8t=n043tO=HL18XJdkXyarMZuFpGgVWprAURAkHN5GkM1?SQZoRL7r/R4xvMZ02vJM")
        )
        access_token = presense_token_encode(presense_secrets, str(self.id))
        presense_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("presense.url", "https://dop-uat.airpresense.tech/access_token={}&patient_id={}")
        )
        action = {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": presense_url.format(access_token, self.id),
        }
        pprint.pprint(action)
        return action
