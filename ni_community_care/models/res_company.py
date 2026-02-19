from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    system_start_date = fields.Date(string="วันที่เริ่มใช้งานระบบ")

    backdate_limit_days = fields.Integer(string="จำนวนวันย้อนหลัง", default=7)
