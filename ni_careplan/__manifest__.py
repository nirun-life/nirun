#  Copyright (c) 2023 NSTDA

{
    "name": "Care Plan",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": [
        "ni_patient",
        "ni_condition",
        "ni_service",
        "ni_goal",
        "ni_document_ref",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ni_careplan_views.xml",
        "views/ni_careplan_category_views.xml",
        "views/ni_encounter_views.xml",
        "views/ni_goal_achievement_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
