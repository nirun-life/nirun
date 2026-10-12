#  Copyright (c) 2021-2023 NSTDA

{
    "name": "Survey - Subject",
    "summary": "Survey subjects and respondent management",
    "version": "19.0.1.0.0",
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
        "views/survey_templates.xml",
        "wizard/survey_subject_views.xml",
    ],
    "assets": {
        "survey.survey_assets": [
            "survey_subject/static/src/js/survey_form.esm.js",
        ],
    },
    "demo": [],
    "application": False,
    "auto_install": False,
    "installable": True,
}
