#  Copyright (c) 2023. NSTDA
import pprint

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .presense_token import presense_token_encode

import logging

_logger = logging.getLogger(__name__)

class Patient(models.Model):
    _inherit = "ni.patient"

    def action_presense_link(self):
        self.ensure_one()
        patient_id = self.id
        presense_secrets = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("presense.secret", "")
        )
        _logger.debug("Creating Patient({}) Link to presense with token({})".format(patient_id, presense_secrets))
        access_token = presense_token_encode(presense_secrets, str(patient_id))
        presense_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("presense.url", "https://dop-uat.airpresense.tech/access/patient?access_token={}&id={}")
        )
        action = {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": presense_url.format(access_token, patient_id),
        }
        return action
