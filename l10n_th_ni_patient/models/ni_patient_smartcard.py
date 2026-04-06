#  Copyright (c) 2024. NSTDA

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
        res = super().create(vals)
        res.link_patient()
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

    @api.constrains("card_data")
    def extract_card_data(self):
        for rec in self:
            if not rec.card_data:
                raise ValidationError(_("Must have card data"))
            rec._extract_card_info()

    def _extract_card_info(self):
        rec = self
        names = rec.card_data.split("#")
        rec.identifier = names[0]
        rec.title_id = self.env["res.partner.title"].search(
            [("name", "=", names[1])], limit=1
        )
        rec.firstname = names[2]
        rec.middle_name = names[3]
        rec.lastname = names[4]

        rec.firstname_en = names[6]
        rec.middle_name_en = names[7]
        rec.lastname_en = names[8]

        rec.street = " ".join([names[i] for i in range(9, 14) if names[i]])
        rec.address = " ".join([names[i] for i in range(9, 17) if names[i]])

        rec.birthdate = self._parse_th_date(names[18])
        rec.card_issue = names[19]
        rec.card_issue_date = self._parse_th_date(names[20])
        rec.card_expire_date = self._parse_th_date(names[21])
        rec.card_ref = names[22]

    @api.model
    def _parse_th_date(self, date_str):
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
