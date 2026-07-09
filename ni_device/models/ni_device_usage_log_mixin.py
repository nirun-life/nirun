from odoo import api, fields, models


class DeviceUsageLogMixin(models.AbstractModel):
    _name = "ni.device.usage.log.mixin"
    _description = "Device Log Mixin"

    device_id = fields.Many2one("ni.device", index=True)

    # -------------------------
    # HOOK (override ได้)
    # -------------------------

    def _prepare_device_log_vals(self):
        self.ensure_one()

        occurrence = False
        if hasattr(self, "occurrence") and self.occurrence:
            occurrence = self.occurrence
        else:
            occurrence = self.create_date or fields.Datetime.now()

        return {
            "device_id": self.device_id.id,
            "patient_id": getattr(self, "patient_id", False) and self.patient_id.id,
            "company_id": getattr(self, "company_id", False) and self.company_id.id,
            "user_id": getattr(self, "user_id", False) and self.user_id.id,
            "res_model": self._name,
            "res_id": self.id,
            "occurrence": occurrence,
            "state": "completed",
        }

    def _prepare_device_log_extra_vals(self):
        """Hook: สำหรับ model เฉพาะ เช่น observation sheet"""
        return {}

    # -------------------------
    # CORE
    # -------------------------

    def _create_device_usage_log(self):
        for rec in self:
            if not rec.device_id:
                continue

            vals = rec._prepare_device_log_vals()
            vals.update(rec._prepare_device_log_extra_vals())

            self.env["ni.device.usage"].create(vals)

    # -------------------------
    # ORM override
    # -------------------------

    @api.model
    def create(self, vals_list):
        records = super().create(vals_list)

        # create log หลังจาก record ถูกสร้างแล้ว (มี id แล้ว)
        records._create_device_usage_log()

        return records

    def write(self, vals):
        result = super().write(vals)

        if "device_id" in vals:
            for rec in self:
                existing = self.env["ni.device.usage"].search(
                    [
                        ("res_model", "=", rec._name),
                        ("res_id", "=", rec.id),
                    ]
                )
                if existing:
                    existing.unlink()

                if rec.device_id:
                    rec._create_device_usage_log()

        return result

    # -------------------------
    # Dev
    # -------------------------

    def action_create_device_log(self):
        for rec in self:
            rec._create_device_usage_log()
