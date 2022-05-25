#  Copyright (c) 2021 Piruin P.

{
    "name": "Questionnaire",
    "version": "13.0.0.2.2",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["nirun_patient", "survey_subject", "survey_scoring", "survey_grading"],
    "data": [
        "security/security.xml",
        "security/rules.xml",
        "security/ir.model.access.csv",
        "wizard/survey_subject_views.xml",
        "views/survey_survey_views.xml",
        "views/survey_user_views.xml",
        "views/patient_views.xml",
        "views/encounter_views.xml",
        "report/patient_survey_latest_views.xml",
        "report/encounter_survey_latest_views.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
