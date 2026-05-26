#  Copyright (c) 2023 NSTDA

{
    "name": "Care Plan : Related Problem Observation (!Obsoleted)",
    "summary": "Obsoleted module: merged into care plan",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "ni_careplan",
        "ni_observation",
    ],
    "data": [
        "views/ni_careplan_views.xml",
        "views/ni_careplan_category_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": False,
}
