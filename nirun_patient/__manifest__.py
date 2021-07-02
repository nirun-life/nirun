#  Copyright (c) 2021 Piruin P.

{
    "name": "Patients",
    "version": "13.0.0.5.1",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun", "hr", "mail"],
    "data": [
        "data/ir_sequence_data.xml",
        "data/location_type_data.xml",
        "data/encounter_admit_data.xml",
        "data/encounter_arrangement_data.xml",
        "data/encounter_class_data.xml",
        "data/encounter_courtesy_data.xml",
        "data/encounter_diet_data.xml",
        "security/patient_group.xml",
        "security/patient_security.xml",
        "security/ir.model.access.csv",
        "views/location_views.xml",
        "views/location_type_views.xml",
        "views/encounter_views.xml",
        "views/encounter_location_views.xml",
        "views/encounter_reason_views.xml",
        "views/encounter_admit_views.xml",
        "views/encounter_arrangement_views.xml",
        "views/encounter_class_views.xml",
        "views/encounter_courtesy_views.xml",
        "views/encounter_diet_views.xml",
        "views/encounter_discharge_views.xml",
        "views/partner_views.xml",
        "views/patient_views.xml",
        "views/patient_menus.xml",
    ],
    "demo": ["data/patient_demo.xml", "data/location_demo.xml"],
    "application": True,
    "auto_install": True,
    "installable": True,
}
