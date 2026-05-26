#  Copyright (c) 2023-2024 NSTDA

{
    "name": "Patients Bulk Encounter",
    "summary": "Bulk encounter and rating operations for multiple patients",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, DADOS, Harit, Kawin",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "ni_practitioner", "rating", "ni_service"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/ni_encounter_bulk_views.xml",
        "views/ni_encounter_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ni_patient_bulk/static/src/views/bulk_views.xml",
            "ni_patient_bulk/static/src/views/bulk_views.esm.js",
        ]
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
