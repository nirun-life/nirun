#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Service(models.Model):
    _inherit = "ni.service"
    approval_id = fields.Many2one("ni.service.event.approval")  # inverse field

    category_id = fields.Many2one(required=True)
    timing_id = fields.Many2one("ni.timing.template", "ความถี่")

    user_id = fields.Many2one("res.users")
    objective = fields.Html("วัตถุประสงค์")
    procedure = fields.Html("ขั้นตอนการดำเนินงาน")
    benefit = fields.Html("ประโยชน์ที่ได้รับ")
    target = fields.Integer("จำนวนเป้าหมาย")
    target_type_ids = fields.Many2many(
        "ni.patient.type",
        "ni_service_target_type",
        "service_id",
        "type_id",
        "กลุ่มเป้าหมาย",
    )
    description = fields.Html("หมายเหตุ")

    category_color = fields.Integer(related="category_id.color")
    my_service = fields.Boolean(
        compute="_compute_my_service", search="_search_my_service"
    )

    @api.depends("user_id")
    def _compute_my_service(self):
        for rec in self:
            rec.my_service = rec.user_id == self.env.user.id

    def _search_my_service(self, operator, operand):
        if operator == "=":
            return [("user_id", "=" if bool(operand) else "!=", self.env.user.id)]
        raise ValidationError(_("my_service support only '=', 'True' or 'False'"))


class ServiceCalendar(models.Model):
    _inherit = "ni.service.event"

    attend_patient_ids = fields.Many2many(
        "ni.patient", "ni_patient_service_attend", check_company=True
    )
