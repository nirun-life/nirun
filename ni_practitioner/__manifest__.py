#  Copyright (c) 2023 NSTDA

{
    "name": "Practitioner",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["hr_skills", "ni_patient"],
    "data": [
        "data/hr_employee_category_data.xml",
        "data/hr_resume_line_type_data.xml",
        "data/hr_resume_line_code_data.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_category_views.xml",
        "views/hr_employee_view.xml",
        "views/hr_resume_line_views.xml",
        "views/hr_resume_line_code_views.xml",
        "views/hr_resume_menu.xml",
        "views/ni_encounter_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/ni_practitioner/static/src/xml/resume_templates.xml",
        ],
    },
    "pre_init_hook": "pre_init_hook",
    "application": False,
    "auto_install": False,
    "installable": True,
}
