#  Copyright (c) 2021 NSTDA

{
    "name": "Condition (Problem)",
    "version": "13.0.0.4.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "data/condition_class_data.xml",
        "security/ir.model.access.csv",
        "security/condition_rules.xml",
        "views/condition_code_views.xml",
        "views/condition_class_views.xml",
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
