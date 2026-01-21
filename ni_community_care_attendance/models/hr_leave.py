from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_date


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    requires_allocation = fields.Selection(
        related="holiday_status_id.requires_allocation", readonly=True
    )

    remaining_leaves = fields.Float(
        string="วันลาคงเหลือ (ที่อนุมัติแล้ว)",
        related="holiday_status_id.remaining_leaves",
        readonly=True,
    )

    virtual_remaining_leaves = fields.Float(
        string="วันลาคงเหลือ",
        related="holiday_status_id.virtual_remaining_leaves",
        readonly=True,
    )

    @api.constrains("date_from", "date_to", "employee_id")
    def _check_date(self):
        if self.env.context.get("leave_skip_date_check", False):
            return

        all_employees = self.all_employee_ids
        all_leaves = self.search(
            [
                ("date_from", "<", max(self.mapped("date_to"))),
                ("date_to", ">", min(self.mapped("date_from"))),
                ("employee_id", "in", all_employees.ids),
                ("id", "not in", self.ids),
                ("state", "not in", ["cancel", "refuse"]),
            ]
        )
        for holiday in self:
            domain = [
                ("date_from", "<", holiday.date_to),
                ("date_to", ">", holiday.date_from),
                ("id", "!=", holiday.id),
                ("state", "not in", ["cancel", "refuse"]),
            ]

            employee_ids = (holiday.employee_id | holiday.employee_ids).ids
            search_domain = domain + [("employee_id", "in", employee_ids)]
            conflicting_holidays = all_leaves.filtered_domain(search_domain)

            if conflicting_holidays:
                conflicting_holidays_list = []
                # Do not display the name of the employee if the conflicting holidays have an employee_id.user_id
                # equivalent to the user id
                holidays_only_have_uid = bool(holiday.employee_id)
                holiday_states = dict(
                    conflicting_holidays.fields_get(allfields=["state"])["state"][
                        "selection"
                    ]
                )
                for conflicting_holiday in conflicting_holidays:
                    conflicting_holiday_data = {}
                    conflicting_holiday_data[
                        "employee_name"
                    ] = conflicting_holiday.employee_id.name
                    conflicting_holiday_data["date_from"] = format_date(
                        self.env, min(conflicting_holiday.mapped("date_from"))
                    )
                    conflicting_holiday_data["date_to"] = format_date(
                        self.env, min(conflicting_holiday.mapped("date_to"))
                    )
                    conflicting_holiday_data["state"] = holiday_states[
                        conflicting_holiday.state
                    ]
                    if conflicting_holiday.employee_id.user_id.id != self.env.uid:
                        holidays_only_have_uid = False
                    if conflicting_holiday_data not in conflicting_holidays_list:
                        conflicting_holidays_list.append(conflicting_holiday_data)
                if not conflicting_holidays_list:
                    return
                conflicting_holidays_strings = []
                if holidays_only_have_uid:
                    for conflicting_holiday_data in conflicting_holidays_list:
                        conflicting_holidays_string = _(
                            "ตั้งแต่วันที่ %(date_from)s ถึงวันที่ %(date_to)s – สถานะ %(state)s",
                            date_from=conflicting_holiday_data["date_from"],
                            date_to=conflicting_holiday_data["date_to"],
                            state=conflicting_holiday_data["state"],
                        )
                        conflicting_holidays_strings.append(conflicting_holidays_string)
                    raise ValidationError(
                        _(
                            "คุณไม่สามารถกำหนดวันลาที่ซ้อนทับกันในวันเดียวกันได้\nการลาที่มีอยู่แล้ว:\n%s"
                        )
                        % ("\n".join(conflicting_holidays_strings))
                    )
                for conflicting_holiday_data in conflicting_holidays_list:
                    conflicting_holidays_string = _(
                        "%(employee_name)s – ตั้งแต่วันที่ %(date_from)s ถึงวันที่ %(date_to)s – สถานะ %(state)s",
                        employee_name=conflicting_holiday_data["employee_name"],
                        date_from=conflicting_holiday_data["date_from"],
                        date_to=conflicting_holiday_data["date_to"],
                        state=conflicting_holiday_data["state"],
                    )
                    conflicting_holidays_strings.append(conflicting_holidays_string)
                conflicting_employees = set(employee_ids) - set(
                    conflicting_holidays.employee_id.ids
                )
                # Only one employee has a conflicting holiday
                if len(conflicting_employees) == len(employee_ids) - 1:
                    raise ValidationError(
                        _(
                            "คุณไม่สามารถกำหนดวันลาที่ซ้อนทับกันในวันเดียวกันสำหรับพนักงานคนเดียวกันได้\nการลาที่มีอยู่แล้ว:\n%s"
                        )
                        % ("\n".join(conflicting_holidays_strings))
                    )
                raise ValidationError(
                    _(
                        "คุณไม่สามารถกำหนดวันลาที่ซ้อนทับกันในวันเดียวกันสำหรับพนักงานกลุ่มเดียวกันได้\nการลาที่มีอยู่แล้ว:\n%s"
                    )
                    % ("\n".join(conflicting_holidays_strings))
                )
