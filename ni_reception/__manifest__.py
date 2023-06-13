#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Reception",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "ni_condition", "ni_allergy"],
    "data": ["views/ni_encounter_views.xml"],
    "assets": {
        "web.assets_backend": [
            "ni_reception/static/src/views/register_views.esm.js",
            "ni_reception/static/src/views/register_views.xml",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
