# Copyright 2025
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Attendance Area Check",
    "summary": """
        ตรวจสอบพื้นที่เช็คอิน/เช็คเอาท์ ว่าตรงกับพื้นที่รับผิดชอบของพนักงานหรือไม่""",
    "version": "16.0.0.1.0",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "depends": ["hr_attendance", "hr_attendance_geolocation"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_attendance_views.xml",
        "views/hr_employee_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_attendance_area_check/static/src/js/attendance_area_check.js",
        ],
    },
}
