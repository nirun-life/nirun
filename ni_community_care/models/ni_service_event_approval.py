import base64
import io
import json
import logging
from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta
from PyPDF2 import PdfMerger

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ServiceEventApproval(models.Model):
    _name = "ni.service.event.approval"
    _inherit = ["mail.thread", "mail.activity.mixin", "ni.identifier.mixin"]
    _rec_name = "identifier"
    _description = "การอนุมัติบันทึกงานผู้บริบาล"

    name = fields.Char(related="identifier", string="ชื่อกิจกรรม")

    _order = "start desc"

    has_pdf = fields.Boolean(string="Has PDF", default=False, readonly=True)
    last_pdf_date = fields.Datetime(string="Last PDF Generated", readonly=True)
    last_pdf_error = fields.Text(string="Last PDF Error", readonly=True)

    city_ids = fields.Many2many(
        comodel_name="res.city",  # เปลี่ยนเป็นโมเดลจริงของคุณ ถ้าไม่ใช่ res.city
        related="user_id.employee_id.city_ids",
        string="เขตพื้นที่รับผิดชอบ",
        readonly=True,
    )

    state_id = fields.Many2one(
        comodel_name="res.country.state", compute="_compute_state_id", store=True
    )

    identifier = fields.Char(
        "หมายเลขอ้างอิง", readonly=True, states={"draft": [("readonly", False)]}
    )
    state = fields.Selection(
        [
            ("pending", "รอการอนุมัติ"),
            ("approved", "อนุมัติแล้ว"),
            ("rejected", "ไม่ผ่านการอนุมัติ"),
        ],
        tracking=True,
        default="pending",
    )

    start = fields.Date(default=fields.Date.context_today)
    stop = fields.Date(default=fields.Date.context_today)

    user_id = fields.Many2one("res.users", string="ผู้บริบาล (User)")
    employee_id = fields.Many2one(
        "hr.employee",
        string="ผู้บริบาล",
        related="user_id.employee_id",
        store=True,
        index=True,
        readonly=True,
    )

    patient_ids = fields.Many2many(
        "ni.patient",
        "ni_service_event_approval_patient",
        "approval_id",
        "patient_id",
        string="Patients",
        compute="_compute_patient_ids",
        store=True,
    )
    patient_count = fields.Integer(compute="_compute_patient_ids", store=True)

    event_ids = fields.Many2many(
        "ni.service.event",
        "ni_service_event_approval_event",
        "approval_id",
        "event_id",
        string="Service Events",
        compute="_compute_service_event",
        store=True,
    )
    event_count = fields.Integer(compute="_compute_service_event", store=True)

    category_ids = fields.Many2many(
        "ni.service.category",
        "ni_service_event_approval_category",
        "approval_id",
        "category_id",
        string="Categories",
        compute="_compute_category_ids",
        store=True,
    )

    category_count = fields.Integer(compute="_compute_category_ids", store=True)

    careplan_ids = fields.Many2many(
        "ni.careplan",
        "ni_service_event_approval_careplan",
        "approval_id",
        "careplan_id",
        string="Care Plans",
        compute="_compute_careplan_ids",
        store=True,
    )
    careplan_count = fields.Integer(compute="_compute_careplan_ids", store=True)

    service_ids = fields.Many2many(
        "ni.service",
        "ni_service_event_approval_service",
        "approval_id",
        "service_id",
        string="Services",
        compute="_compute_service_ids",
        store=True,
    )
    service_count = fields.Integer(compute="_compute_service_ids", store=True)

    start_month_name = fields.Char(
        string="Start Month (TH)", compute="_compute_month_year_thai", store=False
    )
    start_year_thai = fields.Integer(
        string="Start Year (TH)", compute="_compute_month_year_thai", store=False
    )
    stop_month_name = fields.Char(
        string="Stop Month (TH)", compute="_compute_month_year_thai", store=False
    )
    stop_year_thai = fields.Integer(
        string="Stop Year (TH)", compute="_compute_month_year_thai", store=False
    )

    dashboard_data = fields.Text()
    adl_high_count = fields.Integer(
        string="ติดสังคม",
        compute="_compute_adl_counts",
        store=True,
    )
    adl_mid_count = fields.Integer(
        string="ติดบ้าน",
        compute="_compute_adl_counts",
        store=True,
    )
    adl_low_count = fields.Integer(
        string="ติดเตียง",
        compute="_compute_adl_counts",
        store=True,
    )

    @api.depends("patient_ids.type_id.code")
    def _compute_adl_counts(self):
        """นับจำนวนผู้ป่วยแต่ละประเภท"""
        for rec in self:
            high = mid = low = 0
            for p in rec.patient_ids:
                code = p.type_id.code if p.type_id else None
                if code == "adl-high":
                    high += 1
                elif code == "adl-mid":
                    mid += 1
                elif code == "adl-low":
                    low += 1
            rec.adl_high_count = high
            rec.adl_mid_count = mid
            rec.adl_low_count = low

    @api.model
    def get_patient_type_dashboard(self, record_id):
        """อ่านค่าจาก computed fields แทนที่จะคำนวณใหม่"""
        record = self.browse(record_id)
        if not record.exists():
            return {}

        patient_type_status = {
            "adl-high": {
                "description": _("ติดสังคม"),
                "amount": record.adl_high_count,
                "target": 0,
                "class": "text-success",
                "icon": "fa-comments",
            },
            "adl-mid": {
                "description": _("ติดบ้าน"),
                "amount": record.adl_mid_count,
                "target": 0,
                "class": "text-odoo",
                "icon": "fa-home",
            },
            "adl-low": {
                "description": _("ติดเตียง"),
                "amount": record.adl_low_count,
                "target": 0,
                "class": "text-danger",
                "icon": "fa-bed",
            },
        }

        # sync กลับไปยัง dashboard_data ด้วย (เพื่อให้ UI อื่นๆ ใช้ได้)
        record.dashboard_data = json.dumps(patient_type_status, ensure_ascii=False)
        return patient_type_status

    @api.depends("event_ids.service_category_id")
    def _compute_category_ids(self):
        for record in self:
            category_set = record.event_ids.mapped("service_category_id")
            record.category_ids = category_set

            count_map = {}
            for category in category_set:
                count_map[category.id] = len(
                    record.event_ids.filtered(
                        lambda e: e.service_category_id.id == category.id
                    )
                )
            record.category_count = count_map

    @api.depends("user_id", "start", "stop")
    def _compute_service_event(self):
        for rec in self:
            # ค้นหา event ที่ user_id ตรงกับ record นี้
            # และมีช่วงเวลา start-stop ซ้อนทับกับช่วงของ record นี้
            event = self.env["ni.service.event"].search(
                [
                    ("user_id", "=", rec.user_id.id),
                    ("stop", ">=", rec.start),  # event ยังไม่จบก่อน start ของ record
                    ("start", "<=", rec.stop),  # event เริ่มไม่หลัง stop ของ record
                ],
                order="start desc",
            )
            rec.event_ids = event
            rec.event_count = len(event)

    @api.depends("user_id", "start", "stop")
    def _compute_patient_ids(self):
        for record in self:
            domain = [
                ("create_uid", "=", record.user_id.id),
                ("create_date", ">=", record.start),
                ("create_date", "<=", record.stop),
            ]
            patients = self.env["ni.patient"].search(domain)
            record.patient_ids = patients
            record.patient_count = len(patients)

    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)

    @api.depends("identifier")
    def _compute_name(self):
        for rec in self:
            rec.name = rec.identifier

    def action_approved_event(self):
        current_partner = self.env.user.partner_id
        for rec in self:
            rec.state = "approved"

            # ✅ เพิ่ม user_id (ถ้ามี และยังไม่ได้ subscribe)
            if rec.user_id and rec.user_id.partner_id:
                if rec.user_id.partner_id.id not in rec.message_partner_ids.ids:
                    rec.message_subscribe(partner_ids=[rec.user_id.partner_id.id])

            # ✅ เพิ่ม current user (คนกดปุ่ม)
            if current_partner.id not in rec.message_partner_ids.ids:
                rec.message_subscribe(partner_ids=[current_partner.id])

    def action_rejected_event(self):
        current_partner = self.env.user.partner_id
        for rec in self:
            rec.state = "rejected"

            # ✅ เพิ่ม user_id (ถ้ามี และยังไม่ได้ subscribe)
            if rec.user_id and rec.user_id.partner_id:
                if rec.user_id.partner_id.id not in rec.message_partner_ids.ids:
                    rec.message_subscribe(partner_ids=[rec.user_id.partner_id.id])

            # ✅ เพิ่ม current user (คนกดปุ่ม)
            if current_partner.id not in rec.message_partner_ids.ids:
                rec.message_subscribe(partner_ids=[current_partner.id])

    def write(self, vals):
        res = super(ServiceEventApproval, self).write(vals)
        for rec in self:
            if vals.get("user_id"):
                partner = rec.user_id.partner_id
                if partner.id not in rec.message_partner_ids.ids:
                    rec.message_subscribe(partner_ids=[partner.id])
        return res

    @api.depends("city_ids")
    def _compute_state_id(self):
        for rec in self:
            if rec.city_ids:
                # ใช้ city ตัวแรกสุด
                rec.state_id = rec.city_ids[0].state_id.id
            else:
                rec.state_id = False

    @api.depends("user_id", "start", "stop")
    def _compute_careplan_ids(self):
        CarePlan = self.env["ni.careplan"]
        for rec in self:
            domain = [
                ("create_uid", "=", rec.user_id.id),
                ("create_date", ">=", rec.start),
                ("create_date", "<=", rec.stop),
            ]
            rec.careplan_ids = CarePlan.search(domain)
            rec.careplan_count = len(rec.careplan_ids)

    @api.depends("user_id", "start", "stop")
    def _compute_service_ids(self):
        for record in self:
            domain = []

            if record.user_id:
                domain.append(("create_uid", "=", record.user_id.id))
            if record.start:
                domain.append(("create_date", ">=", record.start))
            if record.stop:
                domain.append(("create_date", "<=", record.stop))

            services = self.env["ni.service"].search(domain)
            record.service_ids = services
            record.service_count = len(services)

    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        if "start" in groupby and not orderby:
            orderby = "start desc"
        return super().read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )

    @api.depends("start", "stop")
    def _compute_month_year_thai(self):
        thai_months = {
            1: "มกราคม",
            2: "กุมภาพันธ์",
            3: "มีนาคม",
            4: "เมษายน",
            5: "พฤษภาคม",
            6: "มิถุนายน",
            7: "กรกฎาคม",
            8: "สิงหาคม",
            9: "กันยายน",
            10: "ตุลาคม",
            11: "พฤศจิกายน",
            12: "ธันวาคม",
        }
        for rec in self:
            # Start date
            if rec.start:
                rec.start_month_name = thai_months[rec.start.month]
                rec.start_year_thai = rec.start.year + 543
            else:
                rec.start_month_name = False
                rec.start_year_thai = False

            # Stop date
            if rec.stop:
                rec.stop_month_name = thai_months[rec.stop.month]
                rec.stop_year_thai = rec.stop.year + 543
            else:
                rec.stop_month_name = False
                rec.stop_year_thai = False

    def get_sorted_events(self):
        self.ensure_one()
        patient_event_map = defaultdict(list)

        # loop event
        for ev in sorted(self.event_ids, key=lambda e: e.id):
            for patient in ev.plan_patient_ids:
                patient_event_map[patient].append(ev)

        # อ่านค่าจำกัดจาก ir.config_parameter
        limit_str = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ni_community_care.report_event_limit", "100")
        )
        try:
            limit = int(limit_str)
        except ValueError:
            limit = 100

        result = [
            (patient, patient_event_map[patient]) for patient in patient_event_map
        ][:limit]

        # # 🔴 ดัมมี่ข้อมูลซ้ำเข้าไปเพื่อเทสต์จำนวนหน้า
        # dummy_multiplier = 200  # ปรับได้ เช่น 5, 10, 20
        # result = result * dummy_multiplier
        # _logger.info(
        #     f"Dummy data multiplied {dummy_multiplier}x, total {len(result)} patients in report."
        # )
        # # 🔴เทสต์เสร็จแล้วเอาออกด้วย !!!!!!!!!!
        return result

    def get_sorted_careplans(self):
        self.ensure_one()
        patient_careplan_map = defaultdict(list)

        # loop careplan
        for cp in sorted(self.careplan_ids, key=lambda c: c.id):  # เรียงตาม id
            if cp.patient_id:  # มี patient
                patient_careplan_map[cp.patient_id].append(cp)

        # ล็อกดู dict
        _logger.info("=== Patient Careplan Map ===")
        for patient, careplans in patient_careplan_map.items():
            _logger.info("Patient: %s (id=%s)", patient.name, patient.id)
            for cp in careplans:
                _logger.info("  Careplan: (id=%s)", cp.id)

        # คืนค่า list ของ tuple (patient_record, list_of_careplans) สำหรับ QWeb
        result = [
            (patient, patient_careplan_map[patient]) for patient in patient_careplan_map
        ]
        return result

    def copy(self, default=None):
        default = dict(default or {})
        # reset ฟิลด์ที่ไม่ควร duplicate
        default.update(
            {
                "has_pdf": False,
                "last_pdf_date": False,
                "last_pdf_error": False,
            }
        )
        return super().copy(default)

    def action_regenerate_report(self):
        self._generate_pdf_for_records(self, force_regenerate=True)

    def _generate_pdf_for_records(self, records, force_regenerate=False):
        """
        Helper function สำหรับสร้าง PDF ของ record(s)
        :param records: recordset
        :param force_regenerate: ถ้า True จะลบ attachment เดิมแล้วสร้างใหม่
        """
        report = self.env.ref(
            "ni_community_care.service_event_approval_02_category_action_report_batch"
        )
        if not report:
            _logger.error("Report action not found")
            return

        batch_size_str = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ni_community_care.report_batch_size", "50")
        )
        try:
            batch_size = int(batch_size_str)
        except ValueError:
            batch_size = 50

        for rec_idx, rec in enumerate(records, start=1):
            # เช็คว่า attachment PDF มีอยู่แล้ว
            existing_pdf = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", rec._name),
                    ("res_id", "=", rec.id),
                    ("mimetype", "=", "application/pdf"),
                ],
                limit=1,
            )

            if existing_pdf and not force_regenerate:
                _logger.info(f"[RECORD {rec_idx}] PDF already exists, skip generation")
                continue  # มีไฟล์แล้วไม่ต้องสร้างใหม่

            if existing_pdf and force_regenerate:
                existing_pdf.unlink()
                _logger.info(f"[RECORD {rec_idx}] Old PDF deleted before regeneration")

            # --- ส่วนสร้าง PDF เหมือนเดิม ---
            patient_data = rec.get_sorted_events()
            total_patients = len(patient_data)
            total_batches = (total_patients + batch_size - 1) // batch_size

            pdf_bytes_list = []
            for batch_idx in range(total_batches):
                start = batch_idx * batch_size
                stop = min((batch_idx + 1) * batch_size, total_patients)
                sub_data = patient_data[start:stop]
                _logger.info(
                    f"[RECORD {rec_idx}][BATCH {batch_idx + 1}] patients {start + 1}-{stop}"
                )

                pdf_bytes, _ = (
                    self.env["ir.actions.report"]
                    .with_context(custom_patient_data=sub_data)
                    ._render_qweb_pdf(report.id, [rec.id])
                )
                pdf_bytes_list.append(pdf_bytes)

            merger = PdfMerger()
            for pdf in pdf_bytes_list:
                merger.append(io.BytesIO(pdf))
            merged_pdf = io.BytesIO()
            merger.write(merged_pdf)
            merger.close()

            file_name = f"{rec.name}.pdf"
            self.env["ir.attachment"].create(
                {
                    "name": file_name,
                    "datas": base64.b64encode(merged_pdf.getvalue()),
                    "res_model": rec._name,
                    "res_id": rec.id,
                    "mimetype": "application/pdf",
                }
            )
            rec.sudo().write(
                {
                    "has_pdf": True,
                    "last_pdf_date": fields.Datetime.now(),
                    "last_pdf_error": False,
                }
            )
            _logger.info(
                f"[RECORD {rec_idx}] ✅ Merged PDF saved ({total_patients} patients)"
            )

    def action_refresh_computed_fields(self):
        for rec in self:
            rec._compute_patient_ids()
            rec._compute_service_event()
            rec._compute_category_ids()
            rec._compute_careplan_ids()
            rec._compute_service_ids()
        _logger.info("✅ Recomputed stored fields for %d record(s)", len(self))

    @api.model
    def _cron_create_approvals(self):
        """สร้าง record สำหรับผู้ใช้ทุกคน"""
        # เลื่อนเวลาไปเดือนก่อนหน้า
        today = fields.Date.today()
        prev_month = today - relativedelta(months=1)

        # วันแรกของเดือนก่อนหน้า
        start_date = prev_month.replace(day=1)

        # วันสุดท้ายของเดือนก่อนหน้า
        last_day = start_date + relativedelta(months=1, days=-1)

        # ดึง user ทั้งหมด (กรองได้ถ้าต้องการเฉพาะ group)
        group_user = self.env.ref("ni_patient.group_user")
        group_manager = self.env.ref("ni_patient.group_manager")
        group_admin = self.env.ref("ni_patient.group_admin")

        users = self.env["res.users"].search(
            [
                ("groups_id", "in", [group_user.id]),
                ("groups_id", "not in", [group_manager.id]),
                ("groups_id", "not in", [group_admin.id]),
            ]
        )

        for user in users:
            self.create({"start": start_date, "stop": last_day, "user_id": user.id})

    @api.model
    def _cron_generate_reports_batch(self, **kwargs):
        """
        Generate PDFs for records that do not yet have attachments,
        optionally filtering by months_ago and batch_limit.
        :param months_ago: int, default=0 (0 = all records)
        :param batch_limit: int, default=50
        """
        months_ago = int(kwargs.get("months_ago", 0))
        batch_limit = int(kwargs.get("batch_limit", 50))

        domain = [("has_pdf", "=", False)]

        if months_ago > 0:
            today = datetime.today()
            start_month = today.replace(day=1) - relativedelta(months=months_ago)
            domain.append(("start", ">=", start_month))
            domain.append(("start", "<=", today))
            _logger.info(
                f"[CRON] Filtering records from {start_month.date()} to {today.date()}"
            )
        else:
            _logger.info(
                "[CRON] months_ago=0, processing all records with has_pdf=False"
            )

        records = self.search(domain, limit=batch_limit)
        _logger.info(
            f"[CRON] Found {len(records)} record(s) to generate PDF (batch_limit={batch_limit})."
        )

        self._generate_pdf_for_records(records)

    @api.model
    def _cron_refresh_all_approvals(self):
        approvals = self.search([])  # ดึงทุก record
        approvals.action_refresh_computed_fields()
