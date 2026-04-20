# Copyright 2025
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "NI Community Care — Attendance Area Check",
    "summary": "ตรวจสอบพื้นที่เช็คอิน/เช็คเอาท์การลงเวลางาน",
    "version": "16.0.1.0.0",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "ni_community_care_attendance",
        "hr_attendance",
        "hr_attendance_geolocation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/hr_attendance_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ni_community_care_area_check/static/src/js/attendance_area_check.js",
        ],
    },
}
