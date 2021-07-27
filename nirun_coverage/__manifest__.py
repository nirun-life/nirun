#  Copyright (c) 2021 Piruin P.

{
    "name": "Coverage",
    "version": "13.0.0.1.1",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "security/ir.model.access.csv",
        "data/coverage_type_data.xml",
        "data/coverage_copay_data.xml",
        "views/coverage_type_views.xml",
        "views/coverage_copay_views.xml",
        "views/coverage_views.xml",
        "views/insurance_plan_views.xml",
        "views/patient_views.xml",
        "views/coverage_menu.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
