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
    "depends": [
        "partner_age",
        "partner_gender",
        "ni_patient",
        "ni_condition",
        "ni_allergy",
        "ni_observation",
        "ni_practitioner",
        "ni_coverage",
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "views/ni_encounter_views.xml",
        "views/ni_reception_views.xml",
        "views/ni_reception_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ni_reception/static/src/views/register_views.esm.js",
            "ni_reception/static/src/views/register_views.xml",
        ],
    },
    "application": True,
    "auto_install": False,
    "installable": True,
}
