#  Copyright (c) 2021 NSTDA

{
    "name": "Questionnaire",
    "version": "16.0.0.2.0",
    "development_status": "Alpha",
    "category": "Healthcare",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["ni_patient", "survey", "survey_subject", "survey_grading"],
    "data": [
        "security/res_groups.xml",
        "security/ir_rules.xml",
        "security/ir.model.access.csv",
        "wizard/survey_subject_views.xml",
        "views/survey_survey_views.xml",
        "views/survey_user_input_views.xml",
        "views/ni_patient_views.xml",
        "views/ni_encounter_views.xml",
        "report/ni_patient_survey_latest_views.xml",
        "report/ni_encounter_survey_latest_views.xml",
    ],
    "application": True,
    "auto_install": False,
    "installable": True,
}
