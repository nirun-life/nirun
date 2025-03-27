#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class Need(models.Model):
    _name = "ni.need"
    _description = "Needs"
    _inherit = ["ni.coding"]


class PatientNeedLine(models.Model):
    _name = "ni.patient.need.line"
    _description = "Patient Need Line"
    _inherit = ["ni.patient.res"]
    _rec_name = "need_id"

    need_id = fields.Many2one("ni.need", required=True)
    start = fields.Datetime(default=lambda _: fields.Datetime.now())
    stop = fields.Datetime()
    state = fields.Selection(
        [("active", "ต้องการ"), ("completed", "ได้รับแล้ว"), ("canceled", "ยกเลิก")],
        default="active",
        required=True,
        index=True,
    )
    note = fields.Text("หมายเหตุ")
