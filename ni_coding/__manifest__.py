#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Nirun - Coding",
    "summary": "Base module for clinical coding systems (ICD, SNOMED, LOINC)",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ni_coding_system_data.xml",
        "views/ni_coding_system_views.xml",
        "views/ir_model_views.xml",
        "views/ni_coding_menu.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
