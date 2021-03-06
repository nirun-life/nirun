#  Copyright (c) 2021 Piruin P.

{
    "name": "Care Plans",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun", "nirun_patient", "mail"],
    "data": [
        "security/careplan_group.xml",
        "security/careplan_security.xml",
        "security/ir.model.access.csv",
        "views/careplan_activity_views.xml",
        "views/careplan_category_views.xml",
        "views/careplan_views.xml",
        "views/careplan_menus.xml",
    ],
    "demo": ["data/category_demo.xml"],
    "application": True,
    "auto_install": False,
    "installable": True,
}
