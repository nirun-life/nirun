import base64
import io
import json
import logging
import os
import time
from collections import defaultdict

import psutil
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

    city_ids = fields.Many2many(
        comodel_name="res.city",  # เปลี่ยนเป็นโมเดลจริงของคุณ ถ้าไม่ใช่ res.city
        related="user_id.employee_id.city_ids",
        string="เขตพื้นที่รับผิดชอบ",
        readonly=True,
    )

    state_id = fields.Many2one(
        comodel_name="res.country.state", compute="_compute_state_id"
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

    user_id = fields.Many2one(
        "res.users",
        string="ผู้บริบาล (User)",
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="ผู้บริบาล",
        related="user_id.employee_id",
        store=True,
        index=True,
        readonly=True,
    )

    patient_ids = fields.One2many("ni.patient", compute="_compute_patient_ids")
    patient_count = fields.Integer(compute="_compute_patient_ids")
    event_ids = fields.One2many("ni.service.event", compute="_compute_service_event")
    event_count = fields.Integer(compute="_compute_service_event")

    event_patient_ids = fields.One2many(
        "ni.patient",
        compute="_compute_event_patient_ids",
        string="All Patients (from Events)",
    )
    category_ids = fields.Many2many(
        "ni.service.category", compute="_compute_category_ids"
    )
    category_count = fields.Integer(compute="_compute_category_ids")

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

    # @api.model
    # def create(self, vals):
    #     record = super(ServiceEventApproval, self).create(vals)
    #
    #     # กำหนดเลข id ในรูปแบบ 5 หลัก
    #     id_padded = str(record.id).zfill(5)
    #
    #     # ใช้ start ที่ระบุใน record แทน
    #     if record.start:
    #         date_start = record.start  # ดึงเฉพาะวันที่จาก datetime
    #     else:
    #         # fallback ถ้า start ไม่มีค่า
    #         date_start = fields.Date.context_today(record)
    #
    #     year = date_start.strftime("%Y")
    #     month = date_start.strftime("%m")
    #
    #     # สร้าง identifier
    #     record.identifier = f"AP-{year}{month}{id_padded}"
    #
    #     if vals.get("user_id"):
    #         partner = record.user_id.partner_id
    #         if partner.id not in record.message_partner_ids.ids:
    #             record.message_subscribe(partner_ids=[partner.id])
    #
    #     return record

    def write(self, vals):
        res = super(ServiceEventApproval, self).write(vals)
        for rec in self:
            if vals.get("user_id"):
                partner = rec.user_id.partner_id
                if partner.id not in rec.message_partner_ids.ids:
                    rec.message_subscribe(partner_ids=[partner.id])
        return res

    dashboard_data = fields.Text()

    @api.model
    def get_patient_type_dashboard(self, record_id):
        record = self.browse(record_id)
        all_patients = record.patient_ids
        patient_type_status = {
            "adl-high": {
                "description": _("ติดสังคม"),
                "amount": 0,
                "target": 0,
                "class": "text-success",
                "icon": "fa-comments",
            },
            "adl-mid": {
                "description": _("ติดบ้าน"),
                "amount": 0,
                "target": 0,
                "class": "text-odoo",
                "icon": "fa-home",
            },
            "adl-low": {
                "description": _("ติดเตียง"),
                "amount": 0,
                "target": 0,
                "class": "text-danger",
                "icon": "fa-bed",
            },
        }

        for p in all_patients:
            code = p.type_id.code if p.type_id else None
            if code and code in patient_type_status:
                patient_type_status[code]["amount"] += 1

        record.dashboard_data = json.dumps(patient_type_status, ensure_ascii=False)
        return patient_type_status

    @api.depends("city_ids")
    def _compute_state_id(self):
        for rec in self:
            if rec.city_ids:
                # ใช้ city ตัวแรกสุด
                rec.state_id = rec.city_ids[0].state_id.id
            else:
                rec.state_id = False

    careplan_ids = fields.One2many(
        comodel_name="ni.careplan",
        inverse_name="id",  # dummy inverse
        string="แผนการดูแล",
        compute="_compute_careplan_ids",
        store=False,
    )
    careplan_count = fields.Integer(compute="_compute_careplan_ids", store=False)

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

    service_ids = fields.One2many(
        comodel_name="ni.service",
        inverse_name="id",  # dummy, ต้องใส่อะไรก็ได้
        string="Services",
        compute="_compute_service_ids",
        store=False,
    )

    service_count = fields.Integer(
        string="จำนวน Services",
        compute="_compute_service_ids",
        store=False,
    )

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
        for ev in sorted(self.event_ids, key=lambda e: e.id):  # เรียง event ตาม id
            for patient in ev.plan_patient_ids:  # loop patient ที่อยู่ใน event
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
            limit = 100  # fallback ถ้าค่าที่เก็บไว้ไม่ใช่ตัวเลข
            # คืนค่า list จำกัดตาม limit
        result = [
            (patient, patient_event_map[patient]) for patient in patient_event_map
        ][:limit]
        return result

    # 🔹 ดัมมี่ข้อมูลซ้ำเข้าไปเพื่อเทสต์จำนวนหน้า
    # def get_sorted_events(self):
    #     self.ensure_one()
    #     patient_event_map = defaultdict(list)
    #
    #     # loop event
    #     for ev in sorted(self.event_ids, key=lambda e: e.id):
    #         for patient in ev.plan_patient_ids:
    #             patient_event_map[patient].append(ev)
    #
    #     # อ่านค่าจำกัดจาก ir.config_parameter
    #     limit_str = (
    #         self.env["ir.config_parameter"]
    #         .sudo()
    #         .get_param("ni_community_care.report_event_limit", "100")
    #     )
    #     try:
    #         limit = int(limit_str)
    #     except ValueError:
    #         limit = 100
    #
    #     result = [
    #                  (patient, patient_event_map[patient]) for patient in patient_event_map
    #              ][:limit]
    #
    #     # 🔹 ดัมมี่ข้อมูลซ้ำเข้าไปเพื่อเทสต์จำนวนหน้า
    #     dummy_multiplier = 200  # ปรับได้ เช่น 5, 10, 20
    #     result = result * dummy_multiplier
    #     _logger.info(
    #         f"Dummy data multiplied {dummy_multiplier}x, total {len(result)} patients in report."
    #     )
    #
    #     return result

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

    @api.model
    def _cron_generate_reports_single(self):

        report = self.env.ref(
            "ni_community_care.service_event_approval_02_category_action_report"
        )
        if not report:
            _logger.error("Report action not found")
            return

        all_records = self.search([])
        batch_size = 10

        def log_memory(label):
            try:
                process = psutil.Process(os.getpid())
                mem = process.memory_info().rss / (1024 * 1024)
                _logger.info(f"[MEMORY] {label}: {mem:.2f} MB")
            except Exception:
                pass

        log_memory("Before batch processing")

        for batch_idx in range(0, len(all_records), batch_size):
            batch = all_records[batch_idx : batch_idx + batch_size]
            _logger.info(
                f"[BATCH {batch_idx // batch_size + 1}] Start processing {len(batch)} records"
            )

            for rec in batch:
                start_time = time.time()
                try:
                    pdf_bytes, _ = self.env["ir.actions.report"]._render_qweb_pdf(
                        report_ref=report.id, res_ids=[rec.id]
                    )
                    elapsed = time.time() - start_time
                    size_mb = len(pdf_bytes) / (1024 * 1024)
                    _logger.info(
                        "[BATCH %s] ✅ Generated PDF for %s in %.2fs (%.2fMB)",
                        batch_idx // batch_size + 1,
                        rec.display_name,
                        elapsed,
                        size_mb,
                    )

                except Exception as e:
                    _logger.warning(
                        f"[BATCH {batch_idx // batch_size + 1}] ❌ Failed for {rec.display_name}: {e}"
                    )

            log_memory(f"After batch {batch_idx // batch_size + 1}")

        log_memory("After all batches")
        _logger.info("=== PDF generation cron finished ===")

    @api.model
    def _cron_generate_reports_batch(self):
        report = self.env.ref(
            "ni_community_care.service_event_approval_02_category_action_report_batch"
        )
        if not report:
            _logger.error("Report action not found")
            return

        # อ่านค่าจำกัดจาก ir.config_parameter
        batch_size_str = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ni_community_care.report_batch_size", "50")
        )

        try:
            batch_size = int(batch_size_str)
        except ValueError:
            batch_size = 50  # fallback ถ้าค่าที่เก็บไว้ไม่ใช่ตัวเลข

        records = self.search([])
        for rec_idx, rec in enumerate(records, start=1):
            _logger.info(f"[RECORD {rec_idx}] Generating merged PDF for {rec.name}")
            patient_data = rec.get_sorted_events()
            total_patients = len(patient_data)
            total_batches = (total_patients + batch_size - 1) // batch_size

            pdf_bytes_list = []

            # render batch
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

            # merge PDF
            merger = PdfMerger()
            for pdf in pdf_bytes_list:
                merger.append(io.BytesIO(pdf))
            merged_pdf = io.BytesIO()
            merger.write(merged_pdf)
            merger.close()

            # save attachment
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

            _logger.info(
                f"[RECORD {rec_idx}] ✅ Merged PDF saved ({total_patients} patients)"
            )
