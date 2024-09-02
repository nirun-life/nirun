#  Copyright (c) 2023 NSTDA

{
    "name": "Goal",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Medical",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "ni_observation"],
    "data": [
        "security/ir.model.access.csv",
        "datas/ni_goal_achievement_data.xml",
        "datas/ni_goal_state_data.xml",
        "views/ni_goal_views.xml",
        "views/ni_goal_category_views.xml",
        "views/ni_goal_state_views.xml",
        "views/ni_goal_achievement_views.xml",
        "views/ni_goal_code_views.xml",
        "views/ni_goal_menus.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
