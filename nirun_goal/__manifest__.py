#  Copyright (c) 2021 NSTDA

{
    "name": "Goal",
    "version": "13.0.0.4.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "nirun_condition", "mail"],
    "data": [
        "data/goal_achievement_data.xml",
        "security/ir.model.access.csv",
        "security/goal_rule.xml",
        "wizard/goal_evaluation_wizard_views.xml",
        "views/goal_views.xml",
        "views/goal_achievement_views.xml",
        "views/goal_code_views.xml",
        "views/patient_views.xml",
        "views/encounter_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
