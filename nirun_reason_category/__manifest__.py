#  Copyright (c) 2021-2023. NSTDA

{
    "name": "Reason Category",
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "security/ir.model.access.csv",
        "views/encounter_reason_category_views.xml",
        "views/encounter_reason_views.xml",
        "views/encounter_reason_category_menu.xml",
    ],
    "application": True,
    "auto_install": True,
    "installable": True,
}
