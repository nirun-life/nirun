/** @odoo-module **/

if (typeof odoo !== "undefined" && odoo.define && !odoo.__hr_attendance_area_check_defined__) {
    odoo.__hr_attendance_area_check_defined__ = true;
    odoo.define("hr_attendance_area_check.my_attendances_patch", function (require) {
        var MyAttendances = require("hr_attendance.my_attendances");
        var KioskConfirm = require("hr_attendance.kiosk_confirm");
        var Dialog = require("web.Dialog");
        var session = require("web.session");

        function showAreaWarningDialog(areaResult, onConfirm, onCancel) {
            var actionLabel = areaResult.action_type === "check_in" ? "เช็คอิน" : "เช็คเอาท์";
            var dialog = new Dialog(null, {
                title: "แจ้งเตือนพื้นที่" + actionLabel,
                size: "medium",
                $content: $(
                    "<div>" +
                        "<p><strong>" +
                        actionLabel +
                        "ที่:</strong> " +
                        _.escape(areaResult.area_name) +
                        "</p>" +
                        "<p>ซึ่งอยู่นอกพื้นที่รับผิดชอบ<br/>(" +
                        _.escape(areaResult.responsible_areas) +
                        ")</p>" +
                        "<p>ต้องการยืนยันการ" +
                        actionLabel +
                        "นอกพื้นที่หรือไม่?</p>" +
                        "</div>"
                ),
                buttons: [
                    {
                        text: "ยืนยัน (นอกพื้นที่)",
                        classes: "btn-warning",
                        click: function () {
                            dialog.close();
                            onConfirm();
                        },
                    },
                    {
                        text: "ยกเลิก",
                        classes: "btn-secondary",
                        close: false,
                        click: function () {
                            dialog.close();
                            onCancel();
                        },
                    },
                ],
            });
            dialog.open();
        }

        function doAttendanceRPC(self, employeeId, nextAction, lat, lon, pinBoxVal) {
            return self._rpc({
                model: "hr.employee",
                method: "attendance_manual",
                args: [employeeId, nextAction, pinBoxVal || null],
                context: Object.assign({}, session.user_context, {
                    latitude: lat,
                    longitude: lon,
                }),
            });
        }

        function handleAttendance(self, employeeId, nextAction, lat, lon, pinBoxVal, onWarningCancel) {
            self._rpc({
                model: "hr.employee",
                method: "check_attendance_area",
                args: [employeeId],
                context: Object.assign({}, session.user_context, {latitude: lat, longitude: lon}),
            })
                .then(function (areaResult) {
                    if (areaResult && areaResult.out_of_area) {
                        showAreaWarningDialog(
                            areaResult,
                            function () {
                                // ยืนยัน → ดำเนินการต่อ
                                doAttendanceRPC(self, employeeId, nextAction, lat, lon, pinBoxVal).then(function (result) {
                                    if (result.action) self.do_action(result.action);
                                    else if (result.warning) self.do_warn(result.warning);
                                });
                            },
                            function () {
                                // ยกเลิก → ไม่ทำอะไร
                                if (onWarningCancel) onWarningCancel();
                            }
                        );
                    } else {
                        // ในพื้นที่ หรือ geocode ล้มเหลว → ดำเนินการตามปกติ
                        doAttendanceRPC(self, employeeId, nextAction, lat, lon, pinBoxVal).then(function (result) {
                            if (result.action) self.do_action(result.action);
                            else if (result.warning) self.do_warn(result.warning);
                        });
                    }
                })
                .catch(function () {
                    // RPC ล้มเหลว → ดำเนินการตามปกติ ไม่ block
                    doAttendanceRPC(self, employeeId, nextAction, lat, lon, pinBoxVal).then(function (result) {
                        if (result.action) self.do_action(result.action);
                    });
                });
        }

        MyAttendances.include({
            _manual_attendance: function (position) {
                var self = this;
                handleAttendance(
                    self,
                    [self.employee.id],
                    "hr_attendance.hr_attendance_action_my_attendances",
                    position.coords.latitude,
                    position.coords.longitude,
                    null,
                    null
                );
            },
        });

        KioskConfirm.include({
            _manual_attendance: function (position) {
                var self = this;
                var pinBoxVal = null;
                if (this.pin_pad) {
                    this.$(".o_hr_attendance_pin_pad_button_ok").attr("disabled", "disabled");
                    pinBoxVal = this.$(".o_hr_attendance_PINbox").val();
                }
                handleAttendance(
                    self,
                    [this.employee_id],
                    this.next_action,
                    position.coords.latitude,
                    position.coords.longitude,
                    pinBoxVal,
                    function () {
                        // Reset pin pad เมื่อยกเลิก
                        if (self.pin_pad) {
                            self.$(".o_hr_attendance_PINbox").val("");
                            self.$(".o_hr_attendance_pin_pad_button_ok").removeAttr("disabled");
                        }
                        self.pin_pad = false;
                    }
                );
            },
        });
    });
}
