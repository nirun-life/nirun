from odoo import api, models


class DeviceUsageLogMixin(models.AbstractModel):
    _name = "ni.device.usage.log.mixin"
    _description = "Device Log Mixin"

    # -------------------------
    # HOOK (override ได้)
    # -------------------------

    def _prepare_device_log_vals(self):
        self.ensure_one()

        return {
            "device_id": self.device_id.id,
            "patient_id": getattr(self, "patient_id", False) and self.patient_id.id,
            "company_id": getattr(self, "company_id", False) and self.company_id.id,
            "user_id": self.user_id.id,
            "res_model": self._name,
            "res_id": self.id,
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

            self.env["ni.device.usage.log"].create(vals)

    # -------------------------
    # ORM override
    # -------------------------

    @api.model
    def create(self, vals_list):
        records = super().create(vals_list)

        # create log หลังจาก record ถูกสร้างแล้ว (มี id แล้ว)
        records._create_device_usage_log()

        return records
