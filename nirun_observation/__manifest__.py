#  Copyright (c) 2021 Piruin P.

{
    "name": "Observation",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "mail"],
    "data": [
        "security/observation_group.xml",
        "security/observation_security.xml",
        "security/ir.model.access.csv",
        "data/observation_interpretation_data.xml",
        "data/ni.observation.reference.range.csv",
        "views/interpretation_views.xml",
        "views/reference_range_views.xml",
        "views/vitalsign_views.xml",
        "views/observation_menu.xml",
    ],
    "demo": [],
    "application": True,
    "auto_install": False,
    "installable": True,
}
