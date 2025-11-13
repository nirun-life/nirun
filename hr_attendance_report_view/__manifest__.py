#  Copyright (c) 2025 NSTDA

{
    "name": "HR Employee Attendance Report View",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Human Resources/Employees",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["hr_attendance", "ni_community_care"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rules_data.xml",
        "views/hr_attendance_report_views.xml",
        "views/hr_attendance_missing_report_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
