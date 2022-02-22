#  Copyright (c) 2022 Piruin P.

{
    "name": "Care Plans - Questionnaire",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "nirun_careplan",
        "nirun_questionnaire",
        "nirun_questionnaire_condition",
    ],
    "data": ["views/careplan_views.xml"],
    "application": False,
    "auto_install": True,
    "installable": True,
}
