#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Medication Suggestion",
    "version": "16.0.0.2.0",
    "development_status": "Alpha",
    "category": "Medical/Medication",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_medication"],
    "data": [
        "security/ir.model.access.csv",
        "views/ni_medication_suggest_line_views.xml",
        "views/ni_medication_suggest_views.xml",
        "views/ni_medication_suggest_menu.xml",
        "wizard/ni_medication_suggest_wizard_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
