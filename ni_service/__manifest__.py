#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Service",
    "version": "16.0.0.2.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "ni_patient",
    ],
    "data": [
        "security/ir.model.access.csv",
        "datas/ir_sequence_data.xml",
        "datas/ni_service_category_data.xml",
        "datas/ni_service_type_data.xml",
        "views/ni_service_views.xml",
        "views/ni_encounter_views.xml",
        "views/ni_service_menu.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
