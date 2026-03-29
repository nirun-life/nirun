from odoo import fields, models


class ObservationSheet(models.Model):
    _name = "ni.observation.sheet"
    _inherit = ["ni.observation.sheet", "ni.device.usage.log.mixin"]

    device_id = fields.Many2one("ni.device", index=True, ondelete="restrict")
    user_id = fields.Many2one(
        "res.users", "User", required=True, default=lambda self: self.env.user
    )

    vitalsign_summary = fields.Json(
        compute="_compute_log_summary",
        store=False,
    )

    def _compute_log_summary(self):
        for rec in self:
            result = []
            for ob in rec.observation_ids:
                result.append(
                    {
                        "l": ob.type_id.abbr or ob.type_id.name or "",
                        "v": ob.value,
                        "u": ob.unit_id.name or "",
                        "i": ob.type_id.icon,
                        "color": ob.type_id.icon_color or "#6c757d",
                    }
                )
            rec.vitalsign_summary = result
