#  Copyright (c) 2025 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DeviceUsageLog(models.Model):
    _name = "ni.device.usage.log"
    _description = "Device Usage Log"
    _order = "create_date desc"
    _inherit = ["ni.patient.res", "ni.identifier.mixin", "image.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_id = fields.Many2one(
        "ni.device", required=True, index=True, ondelete="restrict"
    )
    # patient_id = fields.Many2one("ni.patient", copy=False, index=True)
    user_id = fields.Many2one(
        "res.users", "ผู้อ่านบัตร", required=True, default=lambda self: self.env.user
    )
    card_id = fields.Many2one("ni.patient.smartcard", "บัตรประชาชน")
    card_identifier = fields.Char(related="card_id.identifier")

    # link ไปหา sheet (optional — กรณีมาจาก sheet)
    sheet_id = fields.Many2one(
        "ni.observation.sheet", readonly=True, index=True, ondelete="restrict"
    )

    # observations — One2many จริง ไม่ใช่ related
    # รองรับทั้งกรณีมาจาก sheet และกรอกตรงใน log
    observation_ids = fields.One2many(
        "ni.observation", "usage_log_id", string="ผลการตรวจวัด"
    )

    # computed summary สำหรับ kanban — ดึง icon/color จาก type_id โดยตรง
    vitalsign_summary = fields.Json(
        compute="_compute_vitalsign_summary",
        store=False,
    )

    latitude = fields.Float(digits=(10, 7), help="Where the card was reading")
    longitude = fields.Float(digits=(10, 7), help="Where the card was reading")

    def action_gmap_location(self):
        if not self.latitude or not self.longitude:
            raise ValidationError(_("Location coordinates required"))
        http_url = (
            "https://maps.google.com/maps?q=loc:" + self.latitude + "," + self.longitude
        )
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": http_url,
        }

    @api.depends(
        "observation_ids",
        "observation_ids.value",
        "observation_ids.type_id",
        "observation_ids.unit_id",
    )
    def _compute_vitalsign_summary(self):
        for rec in self:
            result = []

            for ob in rec.observation_ids:
                result.append(
                    {
                        "l": ob.type_id.short_name
                        or ob.type_id.name
                        or ob.type_id.code
                        or "",
                        "v": ob.value,
                        "u": ob.unit_id.name or "",
                        "i": ob.type_id.icon,  # 👈 เอา default ออกแล้ว
                        "color": ob.type_id.icon_color or "#6c757d",
                    }
                )

            rec.vitalsign_summary = result or []

    def action_view_sheet(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "ni.observation.sheet",
            "view_mode": "form",
            "res_id": self.sheet_id.id,
        }

    def action_view_smartcard(self):
        self.ensure_one()
        if not self.card_id:
            return False

        return {
            "type": "ir.actions.act_window",
            "res_model": "ni.patient.smartcard",
            "view_mode": "form",
            "res_id": self.card_id.id,
            "target": "new",
            "context": {
                "form_view_initial_mode": "view",
            },
        }
