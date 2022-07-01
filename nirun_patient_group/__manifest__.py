#  Copyright (c) 2021 NSTDA

{
    "name": "Patient Groups",
    "version": "13.0.0.2.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "security/ir.model.access.csv",
        "views/patient_group_views.xml",
        "views/patient_views.xml",
        "views/patient_group_menus.xml",
    ],
    "demo": ["data/patient_group_demo.xml"],
    "application": False,
    "auto_install": False,
    "installable": True,
}
