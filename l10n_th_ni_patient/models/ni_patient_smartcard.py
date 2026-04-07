#  Copyright (c) 2024. NSTDA
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PatientSmartcard(models.Model):
    _name = "ni.patient.smartcard"
    _inherit = "image.mixin"
    _description = "Smart Card Reading Log"
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        copy=False,
        default=lambda self: self.env.user.company_id,
    )
    user_id = fields.Many2one(
        "res.users", "ผู้อ่านบัตร", required=True, default=lambda self: self.env.user
    )
    patient_id = fields.Many2one("ni.patient", copy=False)

    read_date = fields.Date(
        "วันอ่านบัตร", compute="_compute_read_date", store=True, index=True
    )
    reader = fields.Char("เครื่องอ่านบัตร")
    device = fields.Char("อุปกรณ์")
    device_serial_number = fields.Char(string="Serial Number")
    latitude = fields.Float(digits=(10, 7), help="Where the card was reading")
    longitude = fields.Float(digits=(10, 7), help="Where the card was reading")

    card_data = fields.Text(required=True)
    card_expire_date = fields.Date("วันบัตรหมดอายุ")
    card_issue_date = fields.Date("วันออกบัตร")
    card_issue = fields.Char("ที่ออกบัตร")
    card_ref = fields.Char("เลขที่บัตร")

    identifier = fields.Char("เลขประจำตัวประชาชน")
    display_name = fields.Char("ชื่อ-นามสกุล", compute="_compute_display_name")
    title_id = fields.Many2one("res.partner.title", "คำนำหน้า")
    firstname = fields.Char("ชื่อ")
    middle_name = fields.Char("ชื่อกลาง")
    lastname = fields.Char("นามสกุล")
    name = fields.Char("ชื่อ-นามสกุล", compute="_compute_name", copy=True)
    birthdate = fields.Date("วัน/เดือน/ปีเกิด")
    firstname_en = fields.Char("Firstname")
    middle_name_en = fields.Char("Middel Name")
    lastname_en = fields.Char("Lastname")
    address = fields.Char("ที่อยู่")
    street = fields.Char("ถนน", help="Mapping to partner model")

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            data = self.parse_card_data(val.get("card_data"))
            val.update(data)
            if val.get("identifier"):
                patient = self.env["ni.patient"].search(
                    [("identification_id", "=", val.get("identifier"))], limit=1
                )
                if patient:
                    val["patient_id"] = patient.id
        res = super().create(vals)
        return res

    def link_patient(self):
        for rec in self:
            patient = self.env["ni.patient"].search(
                [("identification_id", "=", self.identifier)], limit=1
            )
            if patient:
                rec.patient_id = patient

    @api.depends("firstname", "lastname")
    def _compute_name(self):
        for rec in self:
            rec.name = " ".join([rec.firstname, rec.lastname])

    @api.depends("title_id", "firstname", "middle_name", "lastname")
    def _compute_display_name(self):
        for rec in self:
            names = [rec.title_id.name, rec.firstname, rec.middle_name, rec.lastname]
            rec.display_name = " ".join([n for n in names if n])

    @api.depends("create_date")
    def _compute_read_date(self):
        for rec in self:
            rec.read_date = rec.create_date.date()

    def extract_card_data(self):
        for rec in self:
            if not rec.card_data:
                raise ValidationError(_("Must have card data"))
            val = self.parse_card_data(rec.card_data)
            rec.update(val)

    @api.model
    def parse_card_data(self, card_data: object) -> dict:
        """Parse card_data string into a dict of values."""
        datas = card_data.split("#")
        values = {
            "identifier": datas[0],
            "title_id": self.env["res.partner.title"]
            .search([("name", "=", datas[1])], limit=1)
            .id,
            "firstname": datas[2],
            "middle_name": datas[3],
            "lastname": datas[4],
            "firstname_en": datas[6],
            "middle_name_en": datas[7],
            "lastname_en": datas[8],
            "street": " ".join(
                [datas[i] for i in range(9, 14) if i < len(datas) and datas[i]]
            ),
            "address": " ".join(
                [datas[i] for i in range(9, 17) if i < len(datas) and datas[i]]
            ),
            "birthdate": self._parse_th_date(datas[18]),
            "card_issue": datas[19],
            "card_issue_date": self._parse_th_date(datas[20]),
            "card_expire_date": self._parse_th_date(datas[21]),
            "card_ref": datas[22],
        }
        return values

    @api.model
    def _parse_th_date(self, date_str) -> date:
        year = int(date_str[0:4]) - 543
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        return fields.Date.today().replace(year, month, day)

    def update_to(self, patient=None):
        patient = patient or self.patient_id
        if not patient:
            patient = self.env["ni.patient"].search(
                [("identification_id", "=", self.identifier)], limit=1
            )
        if not patient:
            raise ValidationError(_("Patient Not Found"))
        vals = {
            key: value
            for key, value in self.copy_data()[0].items()
            if key in self.env["ni.patient"]._fields
        }
        patient.update(vals)
        if not self.patient_id:
            self.patient_id = patient
