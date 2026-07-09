from odoo import fields
from odoo.exceptions import UserError

from .common import TestDeviceCommon


class TestDeviceFieldsFromDefinition(TestDeviceCommon):
    def test_manufacturer_copied_from_definition(self):
        self.assertEqual(self.device.manufacturer_id, self.manufacturer)

    def test_model_number_copied_from_definition(self):
        self.assertEqual(self.device.model_number, "BP-100")

    def test_definition_change_updates_model_number(self):
        new_def = self.env["ni.device.definition"].create(
            {"name": "Thermometer", "model_number": "TH-200"}
        )
        self.device.definition_id = new_def
        self.device._compute_from_definition()
        self.assertEqual(self.device.model_number, "TH-200")

    def test_price_copied_from_definition_when_unset(self):
        self.definition.price = 1000
        device = self.env["ni.device"].create(
            {
                "name": "BP Monitor #3",
                "definition_id": self.definition.id,
                "serial_number": "SN-003",
                "received_date": fields.Date.today(),
            }
        )
        self.assertEqual(device.price, 1000)

    def test_price_not_overwritten_when_already_set(self):
        self.definition.price = 1000
        self.device.price = 250
        self.device._compute_from_definition()
        self.assertEqual(self.device.price, 250)

    def test_price_not_resynced_on_definition_change(self):
        self.device.price = 250
        new_def = self.env["ni.device.definition"].create(
            {"name": "Thermometer", "price": 999}
        )
        self.device.definition_id = new_def
        self.device._compute_from_definition()
        self.assertEqual(self.device.price, 250)


class TestDeviceDefinitionLock(TestDeviceCommon):
    def test_definition_id_changeable_before_any_request(self):
        new_def = self.env["ni.device.definition"].create({"name": "Thermometer"})
        self.device.write({"definition_id": new_def.id})
        self.assertEqual(self.device.definition_id, new_def)

    def test_definition_id_locked_after_draft_request(self):
        self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_hold",
                "holder_employee_id": self.employee.id,
            }
        )
        new_def = self.env["ni.device.definition"].create({"name": "Thermometer"})
        with self.assertRaises(UserError):
            self.device.write({"definition_id": new_def.id})

    def test_definition_id_same_value_still_writeable_after_request(self):
        self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_hold",
                "holder_employee_id": self.employee.id,
            }
        )
        self.device.write({"definition_id": self.device.definition_id.id})
        self.assertEqual(self.device.definition_id, self.definition)

    def test_definition_id_locked_after_rejected_request(self):
        req = self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_hold",
                "holder_employee_id": self.employee.id,
            }
        )
        req.action_submit()
        req.with_context(approval_action="reject").action_confirm_approval()
        new_def = self.env["ni.device.definition"].create({"name": "Thermometer"})
        with self.assertRaises(UserError):
            self.device.write({"definition_id": new_def.id})


class TestDeviceDefaults(TestDeviceCommon):
    def test_default_availability_status_is_available(self):
        self.assertEqual(self.device.availability_status, "available")

    def test_default_holding_state_is_available(self):
        self.assertEqual(self.device.state, "available")


class TestDeviceCounts(TestDeviceCommon):
    def test_initial_counts_are_zero(self):
        self.assertEqual(self.device.holder_history_count, 0)
        self.assertEqual(self.device.request_count, 0)
        self.assertEqual(self.device.repair_count, 0)
        self.assertEqual(self.device.usage_count, 0)
        self.assertEqual(self.device.patient_count, 0)

    def test_request_count_increments(self):
        self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_hold",
                "holder_employee_id": self.employee.id,
            }
        )
        self.assertEqual(self.device.request_count, 1)

    def test_repair_count_increments(self):
        self.env["ni.device.repair"].create(
            {
                "device_id": self.device.id,
                "damage_date": fields.Datetime.now(),
            }
        )
        self.assertEqual(self.device.repair_count, 1)


class TestDevicePendingRequest(TestDeviceCommon):
    def _make_request(self, request_type="request_hold", state="draft"):
        req = self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": request_type,
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
            }
        )
        if state == "pending":
            req.state = "pending"
        return req

    def test_no_pending_request_initially(self):
        self.assertFalse(self.device.pending_request_id)

    def test_draft_request_not_counted_as_pending(self):
        self._make_request(state="draft")
        self.device._compute_pending_request()
        self.assertFalse(self.device.pending_request_id)

    def test_pending_request_detected(self):
        req = self._make_request(state="pending")
        self.device._compute_pending_request()
        self.assertEqual(self.device.pending_request_id, req)


class TestDeviceActiveRepair(TestDeviceCommon):
    def test_no_active_repair_initially(self):
        self.assertFalse(self.device.active_repair_id)

    def test_draft_repair_not_active(self):
        self.env["ni.device.repair"].create(
            {"device_id": self.device.id, "damage_date": fields.Datetime.now()}
        )
        self.device._compute_active_repair()
        self.assertFalse(self.device.active_repair_id)

    def test_damaged_state_repair_is_active(self):
        repair = self.env["ni.device.repair"].create(
            {"device_id": self.device.id, "damage_date": fields.Datetime.now()}
        )
        repair.state = "damaged"
        self.device._compute_active_repair()
        self.assertEqual(self.device.active_repair_id, repair)

    def test_completed_repair_not_active(self):
        repair = self.env["ni.device.repair"].create(
            {"device_id": self.device.id, "damage_date": fields.Datetime.now()}
        )
        repair.state = "completed"
        self.device._compute_active_repair()
        self.assertFalse(self.device.active_repair_id)


class TestDeviceNotRepairable(TestDeviceCommon):
    def test_not_repairable_false_when_no_repair(self):
        self.assertFalse(self.device.not_repairable)

    def test_not_repairable_true_when_repair_result_not_repairable(self):
        repair = self.env["ni.device.repair"].create(
            {"device_id": self.device.id, "damage_date": fields.Datetime.now()}
        )
        repair.write({"state": "not_repairable", "repair_result": "not_repairable"})
        self.device._compute_active_repair()
        self.device._compute_is_not_repairable()
        self.assertTrue(self.device.not_repairable)

    def test_not_repairable_false_when_repaired(self):
        repair = self.env["ni.device.repair"].create(
            {"device_id": self.device.id, "damage_date": fields.Datetime.now()}
        )
        repair.write({"state": "completed", "repair_result": "repaired"})
        self.device._compute_active_repair()
        self.device._compute_is_not_repairable()
        self.assertFalse(self.device.not_repairable)


class TestDeviceRepairWorkflow(TestDeviceCommon):
    def setUp(self):
        super().setUp()
        self.repair = self.env["ni.device.repair"].create(
            {"device_id": self.device.id, "damage_date": fields.Datetime.now()}
        )

    def test_action_submit_sets_state_damaged(self):
        self.repair.action_submit()
        self.assertEqual(self.repair.state, "damaged")

    def test_action_submit_marks_device_damaged(self):
        self.repair.action_submit()
        self.assertEqual(self.device.availability_status, "damaged")

    def test_action_confirm_repairing(self):
        self.repair.state = "damaged"
        self.repair.with_context(state_action="repairing").action_confirm()
        self.assertEqual(self.repair.state, "repairing")

    def test_action_confirm_repair_result_repaired(self):
        self.repair.state = "repairing"
        self.repair.repair_result = "repaired"
        self.repair.with_context(state_action="repair_result").action_confirm()
        self.assertEqual(self.repair.state, "completed")
        self.assertEqual(self.device.availability_status, "available")

    def test_action_confirm_repair_result_not_repairable(self):
        self.repair.state = "repairing"
        self.repair.repair_result = "not_repairable"
        self.repair.with_context(state_action="repair_result").action_confirm()
        self.assertEqual(self.repair.state, "not_repairable")
        self.assertEqual(self.device.availability_status, "damaged")


class TestDeviceRequestWorkflow(TestDeviceCommon):
    def _make_hold_request(self):
        req = self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_hold",
                "new_holder_employee_id": self.employee.id,
                "new_holder_partner_id": self.partner.id,
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
            }
        )
        return req

    def _approve_hold(self):
        """Helper: สร้างและอนุมัติ hold request เพื่อให้ device อยู่ใน in_use"""
        req = self._make_hold_request()
        req.action_submit()
        req.with_context(approval_action="approve").action_confirm_approval()
        return req

    def _make_transfer_request(self, new_employee, new_partner):
        req = self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_transfer",
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
                "new_holder_employee_id": new_employee.id,
                "new_holder_partner_id": new_partner.id,
            }
        )
        return req

    def test_approve_dispose_sets_availability_status_disposed(self):
        """อนุมัติ dispose → availability_status ของ device เปลี่ยนเป็น disposed"""
        self._approve_hold()

        dispose_req = self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_dispose",
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
            }
        )
        dispose_req.state = "pending"
        dispose_req.with_context(approval_action="approve").action_confirm_approval()
        self.assertEqual(self.device.availability_status, "disposed")

    # ------------------------------------------------------------------ #
    #  เดิม                                                                #
    # ------------------------------------------------------------------ #

    def test_submit_sets_state_pending(self):
        req = self._make_hold_request()
        req.action_submit()
        self.assertEqual(req.state, "pending")

    def test_submit_hold_sets_device_pending(self):
        req = self._make_hold_request()
        req.action_submit()
        self.assertEqual(self.device.state, "pending")

    def test_approve_hold_sets_device_in_use(self):
        req = self._make_hold_request()
        req.action_submit()
        req.with_context(approval_action="approve").action_confirm_approval()
        self.assertEqual(self.device.state, "in_use")

    def test_approve_hold_creates_holder_history(self):
        req = self._make_hold_request()
        req.action_submit()
        req.with_context(approval_action="approve").action_confirm_approval()
        history = self.env["ni.device.holder"].search(
            [("device_id", "=", self.device.id)]
        )
        self.assertEqual(len(history), 1)

    def test_reject_hold_sets_request_rejected(self):
        req = self._make_hold_request()
        req.action_submit()
        req.with_context(approval_action="reject").action_confirm_approval()
        self.assertEqual(req.state, "rejected")

    def test_reject_hold_restores_device_available(self):
        req = self._make_hold_request()
        req.action_submit()
        req.with_context(approval_action="reject").action_confirm_approval()
        self.assertEqual(self.device.state, "available")

    def test_approve_return_sets_device_available(self):
        self._approve_hold()

        return_req = self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_return",
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
            }
        )
        return_req.state = "pending"
        return_req.with_context(approval_action="approve").action_confirm_approval()
        self.assertEqual(self.device.state, "available")

    def test_approve_dispose_sets_device_disposed(self):
        self._approve_hold()

        dispose_req = self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_dispose",
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
            }
        )
        dispose_req.state = "pending"
        dispose_req.with_context(approval_action="approve").action_confirm_approval()
        self.assertEqual(self.device.state, "disposed")

    def test_approve_transfer_changes_holder(self):
        self._approve_hold()

        new_employee = self.env["hr.employee"].create({"name": "New Holder"})
        new_partner = self.env["res.partner"].create({"name": "New Partner"})

        transfer_req = self._make_transfer_request(new_employee, new_partner)
        transfer_req.state = "pending"
        transfer_req.with_context(approval_action="approve").action_confirm_approval()
        self.assertEqual(self.device.holder_employee_id, new_employee)
        self.assertEqual(self.device.state, "in_use")

    # ------------------------------------------------------------------ #
    #  ใหม่                                                                #
    # ------------------------------------------------------------------ #

    def test_reject_return_keeps_device_in_use(self):
        """ปฏิเสธ return → device ยังคงเป็น in_use"""
        self._approve_hold()

        return_req = self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_return",
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
            }
        )
        return_req.state = "pending"
        return_req.with_context(approval_action="reject").action_confirm_approval()
        self.assertEqual(self.device.state, "in_use")

    def test_reject_transfer_keeps_original_holder(self):
        """ปฏิเสธ transfer → holder_employee_id เป็นคนเดิม และ state ยังเป็น in_use"""
        self._approve_hold()

        new_employee = self.env["hr.employee"].create({"name": "New Holder"})
        new_partner = self.env["res.partner"].create({"name": "New Partner"})

        transfer_req = self._make_transfer_request(new_employee, new_partner)
        transfer_req.state = "pending"
        transfer_req.with_context(approval_action="reject").action_confirm_approval()
        self.assertEqual(self.device.holder_employee_id, self.employee)
        self.assertEqual(self.device.state, "in_use")

    def test_approve_transfer_with_acknowledged_has_acknowledged_date(self):
        """อนุมัติ transfer และผู้ถือครองใหม่ติ๊ก acknowledged → acknowledged_date ต้องมีค่า"""
        self._approve_hold()

        new_employee = self.env["hr.employee"].create({"name": "New Holder"})
        new_partner = self.env["res.partner"].create({"name": "New Partner"})

        transfer_req = self._make_transfer_request(new_employee, new_partner)
        transfer_req.state = "pending"
        transfer_req.write(
            {
                "acknowledged": True,
                "acknowledged_date": fields.Datetime.now(),
            }
        )
        transfer_req.with_context(approval_action="approve").action_confirm_approval()
        self.assertTrue(transfer_req.acknowledged)
        self.assertTrue(transfer_req.acknowledged_date)

    def test_approve_transfer_without_acknowledged_has_no_acknowledged_date(self):
        """อนุมัติ transfer และผู้ถือครองใหม่ไม่ติ๊ก acknowledged → acknowledged_date ต้องไม่มีค่า"""
        self._approve_hold()

        new_employee = self.env["hr.employee"].create({"name": "New Holder"})
        new_partner = self.env["res.partner"].create({"name": "New Partner"})

        transfer_req = self._make_transfer_request(new_employee, new_partner)
        transfer_req.state = "pending"
        transfer_req.with_context(approval_action="approve").action_confirm_approval()
        self.assertFalse(transfer_req.acknowledged)
        self.assertFalse(transfer_req.acknowledged_date)

    def test_submit_request_creates_request_record(self):
        """เมื่อมีการขออนุมัติ ต้องมี record ใน ni.device.request และ query ได้"""
        req = self._make_hold_request()
        req.action_submit()
        records = self.env["ni.device.request"].search(
            [("device_id", "=", self.device.id)]
        )
        self.assertTrue(records)
        self.assertIn(req, records)

    def test_request_count_includes_all_request_types(self):
        """request_count นับรวมทุกประเภท: hold, return, transfer, dispose"""
        self._approve_hold()

        # request_hold ถูกนับไปแล้ว 1 ครั้งจาก _approve_hold
        self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_return",
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
            }
        )
        new_employee = self.env["hr.employee"].create({"name": "Transfer Target"})
        new_partner = self.env["res.partner"].create({"name": "Transfer Partner"})
        self._make_transfer_request(new_employee, new_partner)

        self.env["ni.device.request"].create(
            {
                "device_id": self.device.id,
                "request_type": "request_dispose",
                "holder_employee_id": self.employee.id,
                "holder_partner_id": self.partner.id,
            }
        )
        # รวม: 1 hold + 1 return + 1 transfer + 1 dispose = 4
        self.assertEqual(self.device.request_count, 4)


class TestDeviceRepairCost(TestDeviceCommon):
    def test_repair_cost_sums_all_repairs(self):
        self.env["ni.device.repair"].create(
            [
                {
                    "device_id": self.device.id,
                    "damage_date": fields.Datetime.now(),
                    "repair_cost": 500,
                },
                {
                    "device_id": self.device.id,
                    "damage_date": fields.Datetime.now(),
                    "repair_cost": 300,
                },
            ]
        )
        self.device._compute_repair_cost()
        self.assertEqual(self.device.repair_cost, 800)

    def test_repair_cost_zero_with_no_repairs(self):
        self.device._compute_repair_cost()
        self.assertEqual(self.device.repair_cost, 0)


class TestDeviceDefinitionCounts(TestDeviceCommon):
    def test_definition_device_count(self):
        self.definition._compute_device_count()
        self.assertEqual(self.definition.device_count, 1)

    def test_definition_device_count_increases_with_new_device(self):
        self.env["ni.device"].create(
            {
                "name": "BP Monitor #2",
                "definition_id": self.definition.id,
                "serial_number": "SN-002",
                "received_date": fields.Date.today(),
            }
        )
        self.definition._compute_device_count()
        self.assertEqual(self.definition.device_count, 2)


class TestDeviceDefinitionUsageCount(TestDeviceCommon):
    def test_usage_count_zero_initially(self):
        self.definition._compute_usage_count()
        self.assertEqual(self.definition.usage_count, 0)

    def test_usage_count_reflects_usage_across_devices(self):
        other_device = self.env["ni.device"].create(
            {
                "name": "BP Monitor #2",
                "definition_id": self.definition.id,
                "serial_number": "SN-002",
                "received_date": fields.Date.today(),
            }
        )
        self.env["ni.device.usage"].create({"device_id": self.device.id})
        self.env["ni.device.usage"].create({"device_id": other_device.id})
        self.definition._compute_usage_count()
        self.assertEqual(self.definition.usage_count, 2)


class TestDeviceCreateObservationSheet(TestDeviceCommon):
    def setUp(self):
        super().setUp()
        self.obs_type = self.env["ni.observation.type"].create({"name": "Weight"})
        self.definition.observation_type_ids = [(6, 0, [self.obs_type.id])]
        self.device._compute_from_definition()
        self.patient = self.env["ni.patient"].create({"name": "Test Patient"})

    def test_creates_sheet_with_device_and_lines(self):
        wizard = self.env["ni.device.create.observation.sheet"].create(
            {"device_id": self.device.id, "patient_id": self.patient.id}
        )
        action = wizard.action_confirm()
        sheet = self.env["ni.observation.sheet"].browse(action["res_id"])
        self.assertEqual(sheet.device_id, self.device)
        self.assertEqual(sheet.patient_id, self.patient)
        self.assertEqual(sheet.observation_ids.mapped("type_id"), self.obs_type)

    def test_requires_supported_observation_type(self):
        # _compute_from_definition only fills observation_type_ids from a
        # non-empty definition (see the one-time-fill guard), so clear the
        # device's own field directly rather than via the definition.
        self.device.observation_type_ids = [(5, 0, 0)]
        wizard = self.env["ni.device.create.observation.sheet"].create(
            {"device_id": self.device.id, "patient_id": self.patient.id}
        )
        with self.assertRaises(UserError):
            wizard.action_confirm()


class TestDeviceUsageGeolocation(TestDeviceCommon):
    def test_latitude_longitude_optional(self):
        usage = self.env["ni.device.usage"].create({"device_id": self.device.id})
        self.assertEqual(usage.latitude, 0.0)
        self.assertEqual(usage.longitude, 0.0)

    def test_latitude_longitude_stored(self):
        usage = self.env["ni.device.usage"].create(
            {
                "device_id": self.device.id,
                "latitude": 13.7563,
                "longitude": 100.5018,
            }
        )
        self.assertAlmostEqual(usage.latitude, 13.7563)
        self.assertAlmostEqual(usage.longitude, 100.5018)


class TestDeviceReportLost(TestDeviceCommon):
    def test_report_lost_sets_availability_status_lost(self):
        """เมื่อแจ้งสูญหาย availability_status ต้องเปลี่ยนเป็น lost"""
        self.device.availability_status = "lost"
        self.assertEqual(self.device.availability_status, "lost")

    def test_report_lost_has_lost_date(self):
        """เมื่อแจ้งสูญหาย ต้องมี lost_date บันทึกไว้"""
        self.device.write(
            {
                "availability_status": "lost",
                "lost_date": fields.Datetime.now(),
            }
        )
        self.assertEqual(self.device.availability_status, "lost")
        self.assertTrue(self.device.lost_date)
