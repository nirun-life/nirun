#  Copyright (c) 2021 Piruin P.

{
    "name": "Condition",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "security/ir.model.access.csv",
        "views/condition_code_views.xml",
        "views/condition_type_views.xml",
        "views/condition_views.xml",
        "views/patient_views.xml",
        "views/encounter_views.xml",
        "views/condition_menu.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
