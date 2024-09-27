#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Allergy & Intolerance",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient"],
    "data": [
        "security/ir.model.access.csv",
        "security/ni_allergy_rule.xml",
        "views/ni_patient_views.xml",
        "views/ni_encounter_views.xml",
        "views/ni_allergy_views.xml",
        "views/ni_allergy_code_views.xml",
        "views/ni_allergy_menu.xml",
        "report/summary_report.xml",
    ],
    "demo": [],
    "application": False,
    "auto_install": False,
    "installable": True,
}
