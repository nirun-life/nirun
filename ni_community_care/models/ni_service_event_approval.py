import base64
import io
import logging
from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta
from PyPDF2 import PdfMerger

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

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
        comodel_name="res.city",
        related="user_id.city_ids",
        string="เขตพื้นที่รับผิดชอบ",
        readonly=True,
    )
    state_id = fields.Many2one(
        "res.country.state", "จังหวัด", compute="_compute_state_id", store=True
    )

    identifier = fields.Char("หมายเลขอ้างอิง", readonly=True)
    state = fields.Selection(
        [
            ("pending", "รอการอนุมัติ"),
            ("approved", "อนุมัติแล้ว"),
            ("rejected", "ไม่ผ่านการอนุมัติ"),
            ("archived", "เก็บเป็นประวัติ"),
        ],
        tracking=True,
        default="pending",
        index=True,
    )

    state_date = fields.Datetime(string="วันที่เปลี่ยนสถานะ", readonly=1)
    state_by = fields.Many2one("res.users", string="ผู้อนุมัติ", readonly=1)

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
        context={"active_test": False},
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

    adl_high_count = fields.Integer(
        string="จำนวนผู้สูงอายุประเภทติดสังคม",
        compute="_compute_adl_counts",
        store=True,
    )
    adl_mid_count = fields.Integer(
        string="จำนวนผู้สูงอายุประเภทติดบ้าน",
        compute="_compute_adl_counts",
        store=True,
    )
    adl_low_count = fields.Integer(
        string="จำนวนผู้สูงอายุประเภทติดเตียง",
        compute="_compute_adl_counts",
        store=True,
    )

    adl_unknown_count = fields.Integer(
        string="จำนวนผู้สูงอายุที่ยังไม่ระบุประเภท",
        compute="_compute_adl_counts",
        store=True,
    )

    event_summary_type = fields.Selection(
        [
            ("adl", "แบ่งตามจำนวนผู้สูงอายุที่ได้รับการดูแล"),
            ("category", "แบ่งตามมิติ"),
        ],
        string="การแสดงผล",
        default="adl",
        required=True,
    )

    event_adl_high_count = fields.Integer(
        string="จำนวนผู้สูงอายุประเภทติดสังคมที่เข้าร่วมกิจกรรม",
        compute="_compute_event_adl_counts",
        store=True,
    )
    event_adl_mid_count = fields.Integer(
        string="จำนวนผู้สูงอายุประเภทติดบ้านที่เข้าร่วมกิจกรรม",
        compute="_compute_event_adl_counts",
        store=True,
    )
    event_adl_low_count = fields.Integer(
        string="จำนวนผู้สูงอายุประเภทติดเตียงที่เข้าร่วมกิจกรรม",
        compute="_compute_event_adl_counts",
        store=True,
    )

    event_adl_unknown_count = fields.Integer(
        string="จำนวนผู้สูงอายุที่ยังไม่ระบุประเภทที่เข้าร่วมกิจกรรม",
        compute="_compute_event_adl_counts",
        store=True,
    )

    due_date = fields.Date("กำหนดจ่ายเงิน", help="วันที่คาดว่าจะจ่ายเงิน")

    @api.constrains("due_date")
    def _check_due_date(self):
        for rec in self:
            if rec.due_date and rec.due_date < rec.start:
                raise ValidationError(
                    _(
                        f"กรุณาระบบ '{rec._fields['due_date'].string}' หลังจากวันเริ่มรายงาน {rec.start}"
                    )
                )

    @api.depends("patient_ids.type_id.code")
    def _compute_adl_counts(self):
        """นับจำนวนผู้ป่วยแต่ละประเภท"""
        for rec in self:
            high = mid = low = unknown = 0
            for p in rec.patient_ids:
                code = p.type_id.code if p.type_id else None
                if code == "adl-high":
                    high += 1
                elif code == "adl-mid":
                    mid += 1
                elif code == "adl-low":
                    low += 1
                else:
                    unknown += 1

            rec.adl_high_count = high
            rec.adl_mid_count = mid
            rec.adl_low_count = low
            rec.adl_unknown_count = unknown

    @api.depends("event_ids", "event_ids.plan_patient_ids")
    def _compute_event_adl_counts(self):
        """นับจำนวนผู้เข้าร่วมกิจกรรมแบบไม่ซ้ำ แยกตามประเภทผู้สูงอายุ"""
        for rec in self:
            high = mid = low = unknown = 0

            # รวม id แบบไม่ซ้ำ
            patient_ids = set(rec.event_ids.mapped("plan_patient_ids").ids)

            patients = self.env["ni.patient"].browse(patient_ids)

            for p in patients:
                code = p.type_id.code if p.type_id else None

                if code == "adl-high":
                    high += 1
                elif code == "adl-mid":
                    mid += 1
                elif code == "adl-low":
                    low += 1
                else:
                    unknown += 1

            rec.event_adl_high_count = high
            rec.event_adl_mid_count = mid
            rec.event_adl_low_count = low
            rec.event_adl_unknown_count = unknown

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

            patients = (
                self.env["ni.patient"].with_context(active_test=False).search(domain)
            )

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

    def _subscribe_partners(self):
        """subscribe ผู้เกี่ยวข้อง + คนกดปุ่ม"""
        current_partner = self.env.user.partner_id

        for rec in self:
            partners = []

            if rec.user_id and rec.user_id.partner_id:
                partners.append(rec.user_id.partner_id.id)

            partners.append(current_partner.id)

            partners = list(set(partners) - set(rec.message_partner_ids.ids))
            if partners:
                rec.message_subscribe(partner_ids=partners)

    def action_approved_event(self):
        for rec in self:
            rec.write(
                {
                    "state": "approved",
                    "state_date": fields.Datetime.now(),
                    "state_by": self.env.user.id,
                }
            )

        self._subscribe_partners()

    def action_rejected_event(self):
        for rec in self:
            rec.write(
                {
                    "state": "rejected",
                    "state_date": fields.Datetime.now(),
                    "state_by": self.env.user.id,
                }
            )

        self._subscribe_partners()

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
                _logger.info(
                    f"[RECORD {rec_idx}] (id {rec.id}) PDF already exists, skip generation"
                )
                continue  # มีไฟล์แล้วไม่ต้องสร้างใหม่

            if existing_pdf and force_regenerate:
                existing_pdf.unlink()
                _logger.info(
                    f"[RECORD {rec_idx}] (id {rec.id}) Old PDF deleted before regeneration"
                )

            # --- ส่วนสร้าง Refresh
            rec.action_refresh_computed_fields()

            # --- ส่วนสร้าง PDF
            patient_data = rec.get_sorted_events()
            total_patients = len(patient_data)
            total_batches = (total_patients + batch_size - 1) // batch_size

            pdf_bytes_list = []
            for batch_idx in range(total_batches):
                start = batch_idx * batch_size
                stop = min((batch_idx + 1) * batch_size, total_patients)
                sub_data = patient_data[start:stop]
                _logger.info(
                    f"[RECORD {rec_idx}][BATCH {batch_idx + 1}] (id {rec.id}) patients {start + 1}-{stop}"
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
        today = fields.Date.today()
        prev_month = today - relativedelta(months=1)
        month_start = prev_month.replace(day=1)

        self._create_approvals_by_month_range(
            start_month=month_start,
            end_month=month_start,
            batch_limit=0,  # ไม่ต้อง limit
        )

    @api.model
    def _cron_backfill_approvals(self, **kwargs):
        batch_limit = int(kwargs.get("batch_limit", 500))
        stale_months = int(kwargs.get("stale_months", 6))

        company = self.env.company
        if not company.system_start_date:
            return

        start_month = company.system_start_date.replace(day=1)
        today = fields.Date.today()
        prev_month = today - relativedelta(months=1)
        end_month = prev_month.replace(day=1)

        self._create_approvals_by_month_range(
            start_month=start_month,
            end_month=end_month,
            batch_limit=batch_limit,
        )
        self._cleanup_backfilled_approvals(stale_months=stale_months)

    def _cleanup_backfilled_approvals(self, stale_months=6):
        """
        - ลบ record ที่ field สำคัญว่างหมด
        - เปลี่ยนสถานะเป็น stale ถ้าเก่าเกิน X เดือน
        """

        today = fields.Date.today()
        stale_date = today - relativedelta(months=stale_months)

        # 🔹 1. ลบ record ที่ field ว่างหมด
        fields_to_check = [
            "patient_ids",
            "event_ids",
            "category_ids",
            "careplan_ids",
            "service_ids",
        ]

        domain_empty = []
        for f in fields_to_check:
            domain_empty.append((f, "=", False))

        # AND ทั้งหมด
        empty_records = self.search(domain_empty)

        empty_records.unlink()

        # 🔹 2. เปลี่ยนสถานะเป็น stale
        old_records = self.search(
            [
                ("start", "<", stale_date),
                ("state", "=", "pending"),
            ]
        )

        old_records.write({"state": "archived"})

    @api.model
    def _create_approvals_by_month_range(
        self,
        start_month,
        end_month,
        batch_limit=0,
    ):
        """
        สร้าง approvals ตามช่วงเดือน
        batch_limit = 0  -> ไม่จำกัด
        batch_limit > 0  -> สร้างไม่เกิน N record ต่อรอบ
        """
        batch_limit = int(batch_limit or 0)

        group_user = self.env.ref("ni_patient.group_user")
        group_manager = self.env.ref("ni_patient.group_manager")
        group_admin = self.env.ref("ni_patient.group_admin")

        users = self.env["res.users"].search(
            [
                ("employee_id", "!=", False),
                ("employee_id.active", "=", True),
                ("groups_id", "in", [group_user.id]),
                ("groups_id", "not in", [group_manager.id, group_admin.id]),
            ]
        )

        vals_list = []
        month_cursor = start_month

        while month_cursor <= end_month:

            month_start = month_cursor
            month_end = month_start + relativedelta(months=1, days=-1)

            existing = self.search(
                [
                    ("start", "=", month_start),
                    ("stop", "=", month_end),
                    ("user_id", "in", users.ids),
                ]
            )
            existing_user_ids = set(existing.mapped("user_id").ids)

            for user in users:
                if user.id not in existing_user_ids:
                    vals_list.append(
                        {
                            "start": month_start,
                            "stop": month_end,
                            "user_id": user.id,
                        }
                    )

                    if batch_limit and len(vals_list) >= batch_limit:
                        self.create(vals_list)
                        return len(vals_list)

            month_cursor += relativedelta(months=1)

        if vals_list:
            self.create(vals_list)

        return len(vals_list)

    @api.model
    def _cron_refresh_approvals(self, **kwargs):
        """
        Refresh approvals ตาม limit ที่กำหนด
        """
        batch_limit = int(kwargs.get("batch_limit", 100))
        days_threshold = int(kwargs.get("days_threshold", 7))

        cutoff_date = fields.Datetime.now() - relativedelta(days=days_threshold)

        _logger.info(
            f"[CRON] Refreshing up to {batch_limit} approvals older than {cutoff_date}"
        )

        # search record ตาม limit (เฉพาะที่ยังไม่ approved)
        records = self.search(
            [
                ("write_date", "<", cutoff_date),
                ("state", "!=", "approved"),
            ],
            limit=batch_limit,
        )

        _logger.info(f"[CRON] Found {len(records)} record(s) to refresh.")
        records.action_refresh_computed_fields()
        _logger.info("[CRON] Refresh complete.")

    @api.model
    def _cron_generate_reports_batch(self, **kwargs):
        """
        Generate PDFs for records that do not yet have attachments,
        optionally filtering by retention_months and batch_limit.
        :param retention_months: int, default=0 (0 = all records)
        :param batch_limit: int, default=50
        """
        retention_months = int(kwargs.get("retention_months", 0))
        batch_limit = int(kwargs.get("batch_limit", 50))
        cooldown = int(kwargs.get("cooldown", 1440))

        now = fields.Datetime.now()
        cutoff_date = now - relativedelta(minutes=cooldown)

        _logger.info(
            "[CRON][TIME] now=%s | regenerate_after_days=%s | cutoff_date=%s",
            now,
            cooldown,
            cutoff_date,
        )

        domain = [
            "|",
            ("last_pdf_date", "=", False),
            ("last_pdf_date", "<", cutoff_date),
        ]

        if retention_months > 0:
            today = datetime.today()
            start_month = today.replace(day=1) - relativedelta(months=retention_months)
            domain.append(("start", ">=", start_month))
            _logger.info(f"[CRON] Filtering records from {start_month.date()}")
        else:
            _logger.info(
                "[CRON] months_ago=0, processing all records with has_pdf=False"
            )

        records = self.search(domain, limit=batch_limit)
        _logger.info(
            f"[CRON] Found {len(records)} record(s) to generate PDF (batch_limit={batch_limit})."
        )

        self._generate_pdf_for_records(records, force_regenerate=True)

    @api.model
    def _cron_cleanup_old_reports(self, **kwargs):
        """
        Cleanup old PDF attachments that exceed the retention period.

        :param retention_months: int, number of months to keep reports (default=3)
        :param batch_limit: int, number of records to process per cron run (default=50)
        """
        retention_months = int(kwargs.get("retention_months", 3))
        batch_limit = int(kwargs.get("batch_limit", 50))

        today = fields.Datetime.now()
        cutoff_date = today.replace(day=1) - relativedelta(months=retention_months)

        _logger.info(
            f"[CRON] Cleaning up reports older than {cutoff_date.date()} "
            f"(retention_months={retention_months}, batch_limit={batch_limit})"
        )

        # หา record ที่มีไฟล์และเก่ากว่าระยะเวลาที่กำหนด
        old_records = self.search(
            [("has_pdf", "=", True), ("start", "<", cutoff_date)],
            limit=batch_limit,
        )

        _logger.info(f"[CRON] Found {len(old_records)} old record(s) to clean up.")

        for rec in old_records:
            attachments = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", rec._name),
                    ("res_id", "=", rec.id),
                    ("mimetype", "=", "application/pdf"),
                ]
            )
            if attachments:
                _logger.info(
                    f"[CRON] Removing {len(attachments)} PDF(s) for record ID {rec.id}"
                )
                attachments.unlink()
                rec.has_pdf = False
                rec.last_pdf_date = False

        _logger.info("[CRON] Cleanup complete.")
