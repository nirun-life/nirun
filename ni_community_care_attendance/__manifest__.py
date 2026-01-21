#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Community Care - Attendance",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "ni_community_care",
        "hr_holidays_attendance",
    ],
    "data": [
        "security/ir_rules_data.xml",
        "views/hr_employee_views.xml",
        "views/ni_service_event_approval_views.xml",
        "views/ni_community_care_attendance_menu.xml",
        "views/hr_holidays_views.xml",
        "views/hr_holidays_menu.xml",
        "views/hr_leave_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ni_community_care_attendance/static/src/components/*.js",
            "ni_community_care_attendance/static/src/components/*.xml",
            "ni_community_care_attendance/static/src/views/*.js",
            "ni_community_care_attendance/static/src/views/*.xml",
            "ni_community_care_attendance/static/src/css/calendar_hide_allocation.css",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
