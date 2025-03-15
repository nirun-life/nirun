#  Copyright (c) 2023 NSTDA

{
    "name": "Patient - Website",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "website", "partner_location", "portal"],
    "data": [
        "data/website_data.xml",
        "views/ni_patient_portal.xml",
        "views/ni_patient_portal_templates.xml",
    ],
    "assets": {},
    "application": False,
    "auto_install": False,
    "installable": True,
}
