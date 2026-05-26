#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Thai Coverage",
    "summary": "Thai localization for insurance coverage and benefits",
    "version": "16.0.0.1.1",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "ni_coverage",
    ],
    "data": ["data/ni_coverage_type_data.xml", "views/ni_encounter_views.xml"],
    "application": False,
    "auto_install": False,
    "installable": True,
}
