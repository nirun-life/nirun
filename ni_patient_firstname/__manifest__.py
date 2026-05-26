#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Patients - Firstname and Lastname",
    "summary": "Extended name fields for patient first and last names",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "partner_firstname"],
    "data": [
        "views/ni_patient_views.xml",
    ],
    "application": False,
    "auto_install": True,
    "installable": True,
}
