#  Copyright (c) 2023-2023. NSTDA

{
    "name": "Care Plans Evaluation",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_careplan"],
    "data": [
        "wizard/careplan_eval.xml",
        "views/encounter_view.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}