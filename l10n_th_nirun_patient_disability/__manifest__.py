#  Copyright (c) 2021 NSTDA

{
    "name": "Patients - Disability (Thai Localization)",
    "version": "13.0.0.2.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "OPL-1",
    "maintainers": ["piruin"],
    "depends": ["nirun_condition"],
    "data": [
        "security/ir.model.access.csv",
        "data/disability_data.xml",
        "views/disability_views.xml",
        "views/patient_views.xml",
        "views/encounter_views.xml",
        "views/disability_menus.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
