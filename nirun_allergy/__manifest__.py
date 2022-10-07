#  Copyright (c) 2021 NSTDA

{
    "name": "Allergy & Intolerance",
    "version": "13.0.0.3.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "nirun_medication"],
    "data": [
        "security/ir.model.access.csv",
        "security/allergy_rule.xml",
        "views/patient_views.xml",
        "views/encounter_views.xml",
        "views/allergy_views.xml",
        "views/allergy_code_views.xml",
        "views/allergy_menu.xml",
    ],
    "demo": [],
    "application": False,
    "auto_install": False,
    "installable": True,
}
