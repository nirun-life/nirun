#  Copyright (c) 2021 Piruin P.

{
    "name": "Questionnaire",
    "version": "13.0.0.1.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "survey", "survey_subject"],
    "data": [
        "wizard/survey_subject_views.xml",
        "views/survey_survey_views.xml",
        "views/survey_user_views.xml",
    ],
    "demo": [],
    "application": True,
    "auto_install": False,
    "installable": True,
}
