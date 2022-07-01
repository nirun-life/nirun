#  Copyright (c) 2021 NSTDA

{
    "name": "Observation",
    "version": "13.0.0.3.1",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "mail"],
    "data": [
        "security/observation_group.xml",
        "security/observation_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/observation_interpretation_data.xml",
        "data/observation_category_data.xml",
        "data/observation_type_data.xml",
        "data/observation_reference_range_data.xml",
        "views/interpretation_views.xml",
        "views/reference_range_views.xml",
        "views/observation_type_views.xml",
        "views/observation_category_views.xml",
        "views/observation_views.xml",
        "views/observation_sheet_views.xml",
        "views/observation_menu.xml",
        "views/patient_views.xml",
        "views/encounter_views.xml",
        "report/observation_report_view.xml",
    ],
    "demo": [],
    "application": True,
    "auto_install": False,
    "installable": True,
}
