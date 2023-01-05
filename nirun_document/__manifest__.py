#  Copyright (c) 2021 NSTDA

{
    "name": "Document",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient"],
    "data": [
        "security/ir.model.access.csv",
        "security/document_rule.xml",
        "views/document_category_views.xml",
        "views/document_type_views.xml",
        "views/document_views.xml",
        "views/document_menu.xml",
        "views/encounter_views.xml",
    ],
    "demo": [],
    "application": False,
    "auto_install": False,
    "installable": True,
}
