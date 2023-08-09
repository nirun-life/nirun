#  Copyright (c) 2021 NSTDA

{
    "name": "Patients - Disability (Thai Localization)",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "OPL-1",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "ni_coding"],
    "data": [
        "security/ir.model.access.csv",
        "data/ni_disability_data.xml",
        "views/ni_disability_views.xml",
        "views/ni_patient_views.xml",
        "views/ni_encounter_views.xml",
        "views/ni_disability_menus.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
