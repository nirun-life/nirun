from odoo import _, fields, models
from odoo.exceptions import UserError


class DeviceCreateObservationSheet(models.TransientModel):
    _name = "ni.device.create.observation.sheet"
    _description = "Create Observation Sheet from Device"

    device_id = fields.Many2one("ni.device", required=True, readonly=True)
    patient_id = fields.Many2one("ni.patient", required=True)

    def action_confirm(self):
        self.ensure_one()
        device = self.device_id
        if not device.observation_type_ids:
            raise UserError(
                _(
                    "Cannot create an observation sheet because this device does "
                    "not support any observation types."
                )
            )
        sheet = self.env["ni.observation.sheet"].create(
            {
                "device_id": device.id,
                "patient_id": self.patient_id.id,
                "encounter_id": self.patient_id.encounter_id.id,
                "category_ids": device.observation_type_ids.mapped("category_id").ids,
            }
        )
        sheet.update(
            {
                "observation_ids": [
                    (0, 0, sheet.line_data(obs_type))
                    for obs_type in device.observation_type_ids
                ]
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "ni.observation.sheet",
            "res_id": sheet.id,
            "view_mode": "form",
            "target": "current",
        }
