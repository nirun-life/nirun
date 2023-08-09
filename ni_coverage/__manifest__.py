#  Copyright (c) 2021 NSTDA

{
    "name": "Coverage",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient"],
    "data": [
        "security/ir.model.access.csv",
        "data/coverage_type_data.xml",
        "data/coverage_copay_data.xml",
        "data/ir_sequence_data.xml",
        "views/ni_coverage_type_views.xml",
        "views/ni_coverage_copay_views.xml",
        "views/ni_coverage_views.xml",
        "views/ni_insurance_plan_views.xml",
        "views/ni_patient_views.xml",
        "views/ni_encounter_views.xml",
        "views/ni_coverage_menu.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
