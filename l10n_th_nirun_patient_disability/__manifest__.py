#  Copyright (c) 2021 Piruin P.

{
    "name": "Patients - Disability (Thai Localization)",
    "version": "13.0.0.1.1",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "OPL-1",
    "maintainers": ["piruin"],
    "depends": ["nirun_condition"],
    "data": [
        "security/ir.model.access.csv",
        "data/disability_data.xml",
        "views/disability_views.xml",
        "views/patient_views.xml",
        "views/disability_menus.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
