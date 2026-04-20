/** @odoo-module **/

if (typeof odoo !== "undefined" && odoo.define && !odoo.__ni_community_care_area_check_defined__) {
    odoo.__ni_community_care_area_check_defined__ = true;
    odoo.define("ni_community_care_area_check.my_attendances_patch", function (require) {
        var MyAttendances = require("hr_attendance.my_attendances");
        var KioskConfirm = require("hr_attendance.kiosk_confirm");
        var Dialog = require("web.Dialog");
        var session = require("web.session");

        function showAreaWarningDialog(areaResult, onConfirm, onCancel) {
            var actionLabel = areaResult.action_type === "check_in" ? "เช็คอิน" : "เช็คเอาท์";
            var $noteField = $(
                "<div class='mt-3'>" +
                    "<label class='fw-bold'>หมายเหตุ</label>" +
                    "<textarea class='form-control mt-1 area-warning-note' rows='3' " +
                    "placeholder='ระบุเหตุผลที่" +
                    actionLabel +
                    "นอกพื้นที่...'></textarea>" +
                    "</div>"
            );
            var $content = $(
                "<div>" +
                    "<p><strong>" +
                    actionLabel +
                    "ที่:</strong> " +
                    _.escape(areaResult.area_name) +
                    "</p>" +
                    "<p>ซึ่งอยู่นอกพื้นที่รับผิดชอบ<br/>(" +
                    _.escape(areaResult.responsible_areas) +
                    ")</p>" +
                    "<p class='mb-0'>ต้องการยืนยันการ" +
                    actionLabel +
                    "นอกพื้นที่หรือไม่?</p>" +
                    "</div>"
            );
            $content.append($noteField);

            var dialog = new Dialog(null, {
                title: "แจ้งเตือนพื้นที่" + actionLabel,
                size: "medium",
                $content: $content,
                buttons: [
                    {
                        text: "ยืนยัน (นอกพื้นที่)",
                        classes: "btn-warning",
                        click: function () {
                            var note = dialog.$(".area-warning-note").val().trim();
                            dialog.close();
                            onConfirm(note);
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
                            function (note) {
                                // ยืนยัน → check-in/out จริง
                                doAttendanceRPC(self, employeeId, nextAction, lat, lon, pinBoxVal).then(function (result) {
                                    // บันทึก note ผ่าน Python (sudo) ไม่ใช่ write โดยตรง
                                    if (note) {
                                        self._rpc({
                                            model: "hr.employee",
                                            method: "save_attendance_note",
                                            args: [employeeId, note, areaResult.action_type],
                                            context: session.user_context,
                                        });
                                    }
                                    if (result.action) self.do_action(result.action);
                                    else if (result.warning) self.do_warn(result.warning);
                                });
                            },
                            function () {
                                if (onWarningCancel) onWarningCancel();
                            }
                        );
                    } else {
                        doAttendanceRPC(self, employeeId, nextAction, lat, lon, pinBoxVal).then(function (result) {
                            if (result.action) self.do_action(result.action);
                            else if (result.warning) self.do_warn(result.warning);
                        });
                    }
                })
                .catch(function () {
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
