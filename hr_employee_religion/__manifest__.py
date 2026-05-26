#  Copyright (c) 2023 NSTDA

{
    "name": "HR Employee Religion",
    "summary": "Add religion field to employee records",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Human Resources/Employees",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["hr", "partner_religion"],
    "data": [
        "views/hr_employee_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
