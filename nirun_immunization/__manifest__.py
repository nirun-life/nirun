#  Copyright (c) 2021 NSTDA

{
    "name": "Immunization",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/vaccine_views.xml",
        "views/immunization_views.xml",
        "views/encounter_views.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
