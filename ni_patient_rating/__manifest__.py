#  Copyright (c) 2023 NSTDA

{
    "name": "Patients - Rating",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, DADOS, Harit, Kawin",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "ni_practitioner", "rating"],
    "data": [
        "views/ni_encounter_rating_template.xml",
        "views/ni_encounter_views.xml",
    ],
    "assets": {"web.assets_backend": ["ni_patient_rating/static/src/scss/rating.scss"]},
    "application": False,
    "auto_install": False,
    "installable": True,
}
