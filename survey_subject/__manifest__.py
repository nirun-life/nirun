#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Survey - Subject",
    "version": "16.0.0.2.0",
    "development_status": "Alpha",
    "category": "Marketing/Surveys",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["survey"],
    "data": [
        "security/ir.model.access.csv",
        "views/survey_survey_views.xml",
        "views/survey_user_views.xml",
        "wizard/survey_subject_views.xml",
    ],
    "demo": [],
    "application": False,
    "auto_install": False,
    "installable": True,
}
